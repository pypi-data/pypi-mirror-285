import torch
from torch import optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.model_selection import train_test_split
from nlpx import log_utils


def evaluate(model, eval_loader, device):
	total = 0.0
	losses = 0.0
	correct = 0.0
	model.eval()
	with torch.no_grad():
		for batch in eval_loader:
			batch = [x.to(device) for x in batch]
			# batch = [x.to(device) if torch.is_tensor(x) else x for x in batch]
			y = batch[1]
			loss, logits = model(*batch)
			correct += (logits.argmax(1) == y).sum().item()
			losses += loss.item()
			total += len(y)
	return losses / total, correct / total


class Trainer:

	def __init__(self, model, train_set: Dataset, eval_set: Dataset, collate_fn=None,
				 max_iter=100, optimizer=optim.AdamW, learning_rate=0.001, T_max: int = 0,
				 batch_size=32, eval_batch_size=64,
				 num_workers=0, num_eval_workers=0,
				 pin_memory: bool = False, pin_memory_device: str = "",
				 persistent_workers: bool = False,
				 early_stopping_rounds: int = 10,  # 早停，等10轮决策，评价指标不在变化，停止
	             print_per_rounds: int = 1,
				 device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
				 ):
		self.model = model.to(device)
		self.train_loader = DataLoader(dataset=train_set, batch_size=batch_size, pin_memory=pin_memory,
		                               pin_memory_device=pin_memory_device, persistent_workers=persistent_workers,
		                               num_workers=num_workers, shuffle=True, collate_fn=collate_fn)
		self.eval_loader = DataLoader(dataset=eval_set, batch_size=eval_batch_size,
									  num_workers=num_eval_workers, collate_fn=collate_fn)
		self.max_iter = max_iter
		self.optimizer = optimizer(model.parameters(), lr=learning_rate)
		self.T_max = T_max
		self.early_stopping_rounds = early_stopping_rounds
		self.print_per_rounds = print_per_rounds
		self.device = device

	def train(self):
		cnt = 0
		cnt2 = 0
		best_acc = 0.0
		last_acc = 0.0
		min_loss = 100.0
		best_model = None
		if self.T_max and self.T_max > 0:
			scheduler = CosineAnnealingLR(self.optimizer, T_max=self.T_max)
		for epoch in range(self.max_iter):
			total = 0.0
			losses = 0.0
			correct = 0.0
			self.model.train()
			for batch in self.train_loader:
				batch = [x.to(self.device) for x in batch]
				# batch = [x.to(self.device) if torch.is_tensor(x) else x for x in batch]
				y = batch[1]
				loss, logits = self.model(*batch)
				self.optimizer.zero_grad()
				loss.backward()
				self.optimizer.step()
				if self.T_max and self.T_max > 0:
					scheduler.step()

				losses += loss.item()
				correct += (logits.argmax(1) == y).sum().item()
				total += len(y)

			val_loss, val_acc = evaluate(self.model, self.eval_loader, self.device)
			if self.print_per_rounds == 1:
				self.print(epoch, losses / total, correct / total, val_loss, val_acc)
			elif self.print_per_rounds > 1:
				if epoch % self.print_per_rounds == 0:
					self.print(epoch, losses / total, correct / total, val_loss, val_acc)

			if val_acc > best_acc or (val_acc == best_acc and val_loss < min_loss):
				best_acc = val_acc
				best_model = self.model
				cnt = 0
				cnt2 = 0
				last_acc = val_acc
				best_acc = max(best_acc, val_acc)
				min_loss = min(min_loss, val_loss)
				continue

			if epoch >= min(5, self.early_stopping_rounds) and max(cnt, cnt2) >= self.early_stopping_rounds:  # x次epoch的val_acc不提升或x次epoch的val_acc不变化
				log_utils.info(f"Early stopping at epoch-{epoch}/{self.max_iter}")
				break

			if last_acc == val_acc:  # val_acc不在变化
				cnt2 += 1
			else:
				cnt2 = 0

			cnt += 1
			last_acc = val_acc
			best_acc = max(best_acc, val_acc)
			min_loss = min(min_loss, val_loss)
			
		del self.train_loader, self.eval_loader
		return best_model
	
	def print(self, epoch, loss, correct, val_loss, val_acc):
		log_utils.info(f'epoch-{epoch}/{self.max_iter}  lr: {self.optimizer.param_groups[0]["lr"]:.6f}, '
		               f'train_loss: {loss:.4f}, train_acc: {correct:.4f}, val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f}')


class SimpleTrainer(Trainer):

	def __init__(self, model, X, y, eval_size=0.2, random_state=None, collate_fn=None,
				 max_iter=100, optimizer=optim.AdamW, learning_rate=0.001, T_max: int = 0,
				 batch_size=32, eval_batch_size=64,
				 num_workers=0, num_eval_workers=0,
				 pin_memory: bool = False, pin_memory_device: str = "",
				 persistent_workers: bool = False,
				 early_stopping_rounds=10,  # 早停，等10轮决策，评价指标不在变化，停止
				 print_per_rounds: int = 1,
				 device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')):
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=eval_size, random_state=random_state)
		super().__init__(model,
						 TensorDataset(X_train, y_train),
						 TensorDataset(X_test, y_test),
						 collate_fn,
						 max_iter,
						 optimizer,
						 learning_rate,
						 T_max,
						 batch_size,
						 eval_batch_size,
						 num_workers,
						 num_eval_workers,
						 pin_memory,
						 pin_memory_device,
						 persistent_workers,
						 early_stopping_rounds,
						 print_per_rounds,
						 device
						 )
