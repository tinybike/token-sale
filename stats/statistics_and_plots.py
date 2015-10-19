#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Augur token sale stats and plotting.
@author Jack Peterson (jack@tinybike.net)
"""
from __future__ import division
import json
import datetime
import csv
from decimal import *
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

np.set_printoptions(linewidth=125,
                    suppress=True,
                    formatter={"float": "{: 0.16f}".format})
mpl.style.use("ggplot")
if mpl.is_interactive():
    plt.ioff()

with open("data/fifteen.json") as datafile:
    fifteen = json.load(datafile)
with open("data/ten.json") as datafile:
    ten = json.load(datafile)
with open("data/five.json") as datafile:
    five = json.load(datafile)
with open("data/zero.json") as datafile:
    zero = json.load(datafile)
with open("data/late.json") as datafile:
    late = json.load(datafile)
with open("data/eth-buys.json") as ethfile:
    eth = json.load(ethfile)

with open("data/eth-buys.csv", "w") as ethcsv:
    writer = csv.writer(ethcsv)
    writer.writerow(["index",
                     "Ethereum address",
                     "blocknumber",
                     "timestamp",
                     "bonus",
                     "amount (ether)"])
    for buy in eth.values():
        for b in buy:
            writer.writerow([b["index"],
                             b["address"],
                             b["blocknumber"],
                             str(datetime.datetime.utcfromtimestamp(b["timestamp"]) - datetime.timedelta(hours=4)),
                             b["group"],
                             b["amount"]])

total = Decimal(0)
buys = []
amounts = []
timestamps = []
finalAmounts = {}
totalAdjusted = Decimal(0)
ref = {}
for group in (fifteen, ten, five, zero, late):
    for buy in group:
        total += Decimal(buy["amount"])
        buys.append(buy)
        if buy["referral"] != 0:
            if buy["referral"] in ref:
                ref[buy["referral"]] += Decimal(buy["amount"])
            else:
                ref[buy["referral"]] = Decimal(buy["amount"])
        if buy["accountID"] in finalAmounts:
            finalAmounts[buy["accountID"]] += Decimal(buy["adjusted_amount"])
        else:
            finalAmounts[buy["accountID"]] = Decimal(buy["adjusted_amount"])
        totalAdjusted += Decimal(buy["adjusted_amount"])
        t = datetime.datetime.utcfromtimestamp(buy["timestamp"]) - datetime.timedelta(hours=4)
        if t.month < 8 or (t.month == 8 and t.day < 15):
            print buy
        else:
            amounts.append(float(buy["amount"]))
            timestamps.append(t)
buys = np.array(buys)
for r in ref:
    ref[r] = str(ref[r])
for key in finalAmounts:
    finalAmounts[key] = str(finalAmounts[key])
print "Total:   ", str(total), "BTC"
print "Adjusted:", str(totalAdjusted), "BTC"
print "Expected: 18830.16363 BTC"
print
print "Referrals:"
print json.dumps(ref, indent=4, sort_keys=True)
print

totalEth = Decimal(0)
totalAdjustedEth = Decimal(0)
finalEthAmounts = {}
ethBuys = []
ethAmounts = []
ethTimestamps = []
ethTotalFifteen = Decimal(0)
ethFifteenArray = []
ethTotalTen = Decimal(0)
ethTenArray = []
ethTotalFive = Decimal(0)
ethFiveArray = []
ethTotalZero = Decimal(0)
ethZeroArray = []
ethTotalLate = Decimal(0)
ethLateArray = []
for a, b in eth.items():
    for buy in b:
        totalEth += Decimal(buy["amount"])
        if buy["group"] == "late":
            buy["adjusted_amount"] = buy["amount"]
        if buy["address"] in finalEthAmounts:
            finalEthAmounts[buy["address"]] += Decimal(buy["adjusted_amount"])
        else:
            finalEthAmounts[buy["address"]] = Decimal(buy["adjusted_amount"])
        totalAdjustedEth += Decimal(buy["adjusted_amount"])
        ethBuys.append(buy)
        ethAmounts.append(float(buy["amount"]))
        t = datetime.datetime.utcfromtimestamp(buy["timestamp"]) - datetime.timedelta(hours=4)
        ethTimestamps.append(t)
        if buy["group"] == "15%":
            ethTotalFifteen += Decimal(buy["amount"])
            ethFifteenArray.append(float(buy["amount"]))
        elif buy["group"] == "10%":
            ethTotalTen += Decimal(buy["amount"])
            ethTenArray.append(float(buy["amount"]))
        elif buy["group"] == "5%":
            ethTotalFive += Decimal(buy["amount"])
            ethFiveArray.append(float(buy["amount"]))
        elif buy["group"] == "0%":
            ethTotalZero += Decimal(buy["amount"])
            ethZeroArray.append(float(buy["amount"]))
        else:
            ethTotalLate += Decimal(buy["amount"])
            ethLateArray.append(float(buy["amount"]))
ethBuys = np.array(ethBuys)
for key in finalEthAmounts:
    finalEthAmounts[key] = str(finalEthAmounts[key])
print "Total:   ", str(totalEth), "ETH"
print "Adjusted:", str(totalAdjustedEth), "ETH"
print "Expected: 1176816.436 ETH"
print

with open("data/btc_adjusted_amounts.json", "w") as btcfile:
    json.dump(finalAmounts, btcfile, indent=4, sort_keys=True)

with open("data/eth_adjusted_amounts.json", "w") as ethfile:
    json.dump(finalEthAmounts, ethfile, indent=4, sort_keys=True)

totalFifteen = 0
fifteenArray = []
for buy in fifteen:
    totalFifteen += Decimal(buy["amount"])
    fifteenArray.append(float(buy["amount"]))
fifteenArray = np.array(fifteenArray)
print "15% bonus:", np.mean(fifteenArray), "+/-", np.std(fifteenArray), "BTC"
print len(fifteenArray), "purchases"
print "Total bought:", str(totalFifteen), "BTC"
print "15% bonus:", np.mean(ethFifteenArray), "+/-", np.std(ethFifteenArray), "ETH"
print len(ethFifteenArray), "purchases"
print "Total bought:", str(ethTotalFifteen), "ETH"
print

totalTen = 0
tenArray = []
for buy in ten:
    totalTen += Decimal(buy["amount"])
    tenArray.append(float(buy["amount"]))
tenArray = np.array(tenArray)
print "10% bonus:", np.mean(tenArray), "+/-", np.std(tenArray), "BTC"
print len(tenArray), "purchases"
print "Total bought:", str(totalTen), "BTC"
print "10% bonus:", np.mean(ethTenArray), "+/-", np.std(ethTenArray), "ETH"
print len(ethTenArray), "purchases"
print "Total bought:", str(ethTotalTen), "ETH"
print

totalFive = 0
fiveArray = []
for buy in five:
    totalFive += Decimal(buy["amount"])
    fiveArray.append(float(buy["amount"]))
fiveArray = np.array(fiveArray)
print "5% bonus:", np.mean(fiveArray), "+/-", np.std(fiveArray), "BTC"
print len(fiveArray), "purchases"
print "Total bought:", str(totalFive), "BTC"
print "5% bonus:", np.mean(ethFiveArray), "+/-", np.std(ethFiveArray), "ETH"
print len(ethFiveArray), "purchases"
print "Total bought:", str(ethTotalFive), "ETH"
print

totalZero = 0
zeroArray = []
for buy in zero:
    totalZero += Decimal(buy["amount"])
    zeroArray.append(float(buy["amount"]))
zeroArray = np.array(zeroArray)
print "0% bonus:", np.mean(zeroArray), "+/-", np.std(zeroArray), "BTC"
print len(zeroArray), "purchases"
print "Total bought:", str(totalZero), "BTC"
print "0% bonus:", np.mean(ethZeroArray), "+/-", np.std(ethZeroArray), "ETH"
print len(ethZeroArray), "purchases"
print "Total bought:", str(ethTotalZero), "ETH"
print

totalLate = 0
lateArray = []
for buy in late:
    totalLate += Decimal(buy["amount"])
    lateArray.append(float(buy["amount"]))
lateArray = np.array(lateArray)
print "Late buys:", np.mean(lateArray), "+/-", np.std(lateArray), "BTC"
print len(lateArray), "purchases"
print "Total bought:", str(totalLate), "BTC"
print "Late buys:", np.mean(ethLateArray), "+/-", np.std(ethLateArray), "ETH"
print len(ethLateArray), "purchases"
print "Total bought:", str(ethTotalLate), "ETH"
print

plt.figure()
plt.axis("normal")
ax = plt.gca()
ax2 = ax.twinx()
ax.plot(timestamps, amounts, 'o', color="darkorange")
ax2.plot(ethTimestamps, ethAmounts, 'd', color="blue")
ax.set_ylabel("BTC", fontsize=20, color="darkorange")
ax2.set_ylabel("ETH", fontsize=20, color="blue")
ax.grid = True
plt.title("Augur token sale", fontsize=20, color="black")
plt.show()

btcGini = sum([i*r for (i,r) in enumerate(sorted(amounts))]) / sum(amounts)
btcGini *= 2 / len(amounts)
btcGini -= 1 + 1 / len(amounts)
print "Gini coefficient (BTC buyins):", btcGini

ethGini = sum([i*r for (i,r) in enumerate(sorted(ethAmounts))]) / sum(ethAmounts)
ethGini *= 2 / len(ethAmounts)
ethGini -= 1 + 1 / len(ethAmounts)
print "Gini coefficient (ETH buyins):", ethGini

with open("data/btc-vs-time.csv", "w") as csvfile:
    for t, a in zip(timestamps, amounts):
        print >> csvfile, str(t) + "," + str(a)

with open("data/eth-vs-time.csv", "w") as csvfile:
    for t, a in zip(ethTimestamps, ethAmounts):
        print >> csvfile, str(t) + "," + str(a)

with open("data/referrals.json", "w") as reffile:
    json.dump(ref, reffile)

with open("data/btc-amounts.csv", "w") as csvfile:
    print >> csvfile, ",".join([str(amount) for amount in amounts])

with open("data/eth-amounts.csv", "w") as csvfile:
    print >> csvfile, ",".join([str(amount) for amount in ethAmounts])

plt.subplots(1, 2)

plt.subplot(1, 2, 1)
n, bins, patches = plt.hist(amounts, 175, normed=0, histtype='stepfilled')
plt.setp(patches, 'facecolor', 'darkorange', 'alpha', 0.75)
plt.xlim([10**-1, np.max(amounts)*1.1])
plt.xscale("log")
plt.yscale("log")
plt.xlabel("BTC", fontsize=14)
plt.ylabel("number of purchases", fontsize=14)

plt.subplot(1, 2, 2)
n, bins, patches = plt.hist(ethAmounts, 175, normed=0, histtype='stepfilled')
plt.setp(patches, 'facecolor', 'darkblue', 'alpha', 0.75)
plt.xlim([10, np.max(ethAmounts)*1.1])
plt.xscale("log")
plt.yscale("log")
plt.xlabel("ETH", fontsize=14)
plt.ylabel("number of purchases", fontsize=14)

plt.show()
