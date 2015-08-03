data Funders[](address, amount, blockNum)

data funderNum

data addrToFunderNum[]

data augurAddress

data deadline

def init():
	self.augurAddress = tx.origin
	self.deadline = 47

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
	return(self.Funders[self.addrToFunderNum[address]].amount)

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