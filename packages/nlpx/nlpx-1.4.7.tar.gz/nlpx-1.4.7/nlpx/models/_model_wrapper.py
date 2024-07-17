import torch
import numpy as np
import pandas as pd
from torch import optim
from pathlib import Path
from typing import Union, List
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset, Dataset

from nlpx.llm import TokenizeVec
from nlpx.text_token import TokenEmbedding
from nlpx.training import Trainer, SimpleTrainer, evaluate


class ModelWrapper:

	def __init__(self, model_path: Union[str, Path] = None, classes: List[str] = None,
					device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')):
		self.classes = classes
		self.device = device
		self.model = torch.load(model_path, map_location=device) if model_path else None

	def train(self, model, train_set: Dataset, eval_set: Dataset, collate_fn=None, max_iter=100,
				optimizer=optim.AdamW, learning_rate=0.001, T_max: int = 0,
				batch_size=32, eval_batch_size=64,
				num_workers=0, num_eval_workers=0,
                pin_memory: bool = False, pin_memory_device: str = "",
                persistent_workers: bool = False,
				early_stopping_rounds: int = 10,
	            print_per_rounds: int = 1):
		trainer = Trainer(model, train_set, eval_set, collate_fn,
						  max_iter, optimizer, learning_rate, T_max,
						  batch_size, eval_batch_size,
						  num_workers, num_eval_workers,
						  pin_memory, pin_memory_device,
		                  persistent_workers,
						  early_stopping_rounds,  # 早停，等10轮决策，评价指标不在变化，停止
						  print_per_rounds,
						  self.device)
		self.model = trainer.train()

	def predict(self, X: torch.Tensor):
		logits = self.logits(X)
		return logits.argmax(1)

	def predict_classes(self, X: torch.Tensor):
		assert self.classes is not None, 'classes must be specified'
		pred = self.predict(X)
		return [self.classes[i] for i in pred.detach().numpy().ravel()]

	def predict_proba(self, X: torch.Tensor):
		logits = self.logits(X)
		result = F.softmax(logits, dim=1).max(1)
		return result.indices, result.values

	def predict_classes_proba(self, X: torch.Tensor):
		assert self.classes is not None, 'classes must be specified'
		indices, values = self.predict_proba(X)
		return [self.classes[i] for i in indices.detach().numpy().ravel()], values

	def logits(self, X: torch.Tensor):
		self.model.eval()
		with torch.no_grad():
			logits = self.model(X)
		return logits

	def evaluate(self, eval_set: Dataset, batch_size=16, num_workers=0, max_length: int = 0,  collate_fn=None):
		eval_loader = DataLoader(dataset=eval_set, batch_size=batch_size,
								 num_workers=num_workers, collate_fn=collate_fn)
		_, acc = evaluate(self.model, eval_loader, self.device)
		return acc

	def save(self, model_path: Union[str, Path] = './best_model.pt'):
		torch.save(model_path, self.model)

	def load(self, model_path: Union[str, Path] = './best_model.pt'):
		self.model = torch.load(model_path, map_location=self.device)


class SimpleModelWrapper(ModelWrapper):

	def __init__(self, tokenize_vec: Union[TokenizeVec, TokenEmbedding], model_path: Union[str, Path] = None,
				 classes: List[str] = None, device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')):
		super().__init__(model_path, classes, device)
		self.tokenize_vec = tokenize_vec

	def train(self, model, texts: Union[List[str], np.ndarray, pd.Series], y: Union[torch.LongTensor, List, np.ndarray],
			  max_length: int = 0, eval_size=0.2, random_state=None, collate_fn=None,max_iter=100,
			  optimizer=optim.AdamW, learning_rate=0.001, T_max: int = 0,
			  batch_size=32, eval_batch_size=64,
			  num_workers=0, num_eval_workers=0,
              pin_memory: bool = False, pin_memory_device: str = "",
              persistent_workers: bool = False,
			  early_stopping_rounds: int = 10,
	          print_per_rounds: int = 1, n_jobs=-1, cut_fn=None):
		X = self.get_vec(texts, max_length=max_length, n_jobs=n_jobs)
		if isinstance(y, List) or isinstance(y, np.ndarray):
			y = torch.tensor(y, dtype=torch.long)
		trainer = SimpleTrainer(model, X, y, eval_size, random_state, collate_fn,
								 max_iter, optimizer, learning_rate, T_max,
								 batch_size, eval_batch_size,
								 num_workers, num_eval_workers,
							     pin_memory, pin_memory_device,
			                     persistent_workers,
								 early_stopping_rounds,
								 print_per_rounds,
								 self.device)
		self.model = trainer.train()

	def predict(self, texts: List[str], max_length: int = 0, n_jobs=-1, cut_fn=None):
		logits = self.logits(texts, max_length, n_jobs=n_jobs, cut_fn=cut_fn)
		return logits.argmax(1)

	def predict_classes(self, texts: List[str], max_length: int = 0, n_jobs=-1, cut_fn=None):
		assert self.classes is not None, 'classes must be specified'
		pred = self.predict(texts, max_length, n_jobs=n_jobs, cut_fn=cut_fn)
		return [self.classes[i] for i in pred.detach().numpy().ravel()]
	
	def predict_proba(self, texts: List[str], max_length: int = 0, n_jobs=-1, cut_fn=None):
		logits = self.logits(texts, max_length, n_jobs=n_jobs, cut_fn=cut_fn)
		result = F.softmax(logits, dim=1).max(1)
		return result.indices, result.values

	def predict_classes_proba(self, texts: List[str], max_length: int = 0, n_jobs=-1, cut_fn=None):
		assert self.classes is not None, 'classes must be specified'
		indices, values = self.predict_proba(texts, max_length, n_jobs, cut_fn=cut_fn)
		return [self.classes[i] for i in indices.detach().numpy().ravel()], values

	def logits(self, texts: List[str], max_length: int = 0, n_jobs=-1, cut_fn=None):
		X = self.get_vec(texts, max_length, n_jobs=n_jobs, cut_fn=cut_fn)
		return super().logits(X)

	def evaluate(self, texts: Union[str, List[str], np.ndarray, pd.Series], y: Union[torch.LongTensor, List, np.ndarray], batch_size=16, num_workers=0,
				 max_length: int = 0, collate_fn=None, n_jobs=-1, cut_fn=None):
		X = self.get_vec(texts, max_length, n_jobs=n_jobs, cut_fn=cut_fn)
		if isinstance(y, List) or isinstance(y, np.ndarray):
			y = torch.tensor(y, dtype=torch.long)
		eval_set = TensorDataset(X, y)
		return super().evaluate(eval_set, batch_size=batch_size, num_workers=num_workers, collate_fn=collate_fn)

	def get_vec(self, texts: Union[str, List[str], np.ndarray, pd.Series], max_length: int, n_jobs: int, cut_fn=None):
		if isinstance(texts, str):
			texts = [texts]

		if isinstance(self.tokenize_vec, TokenizeVec):
			return self.tokenize_vec.parallel_encode_plus(texts, max_length=max_length, padding='max_length',
															truncation=True, add_special_tokens=True,
															return_token_type_ids=True,return_attention_mask=True,
															return_tensors='pt', n_jobs=n_jobs)
		elif isinstance(self.tokenize_vec, TokenEmbedding):
			return self.tokenize_vec(texts, max_length, cut_fn=cut_fn)

		raise ValueError("Invalid tokenize_vec, it must be a TokenizeVec or TokenEmbedding.")
