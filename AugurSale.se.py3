data Funders[](address, amount, blockNum)

data funderNum

data addrToFunderNum[]

data augurAddress

data deadline

def init():
	self.augurAddress = 0xa04fc9bd2be8bcc6875d9ebb964e8f858bcc1b4f
	self.deadline = 432015

def buyRep():
	if(msg.value==0):
		return(0)
	if(block.number < self.deadline):
		send(self.augurAddress, msg.value)
		self.Funders[self.funderNum].amount = msg.value
		self.Funders[self.funderNum].blockNum = block.number
		self.Funders[self.funderNum].address = tx.origin
		self.addrToFunderNum[tx.origin] = self.funderNum
		self.funderNum += 1
		return(1)
	else:
		return(0)

def getAmountSent(address):
	amount = 0
	i = 0
	while i < self.funderNum:
		if address == self.Funders[i].address:
			amount += self.Funders[i].amount
		i += 1
	return(amount)

def getBlockNumSent(address):
	return(self.Funders[self.addrToFunderNum[address]].blockNum)

def getFunderNum():
	return(self.funderNum)

def getAmtByIndex(index):
	return(self.Funders[index].amount)

def getAddrByIndex(index):
	return(self.Funders[index].address)

def getBlockNumByIndex(index):
	return(self.Funders[index].blockNum)

def addrToFunder(address):
	return(self.addrToFunderNum[address])

def getFundsRaised():
	return(self.augurAddress.balance)
