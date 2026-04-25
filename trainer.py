
def runSearch(algo, start_state, goal_state, nn=None):
    trainer = L.Trainer(limit_train_batches=100, max_epochs=1)
    trainer.fit(model=nn, train_dataloaders=train_loader)