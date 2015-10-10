#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Getting Augur's token sale data organized...
@author Jack Peterson (jack@tinybike.net)
"""
from __future__ import division
import sys
import getopt
import csv
import json
import datetime
import requests
from decimal import *

API = "https://blockchain.info/rawaddr/"
MULTISIG_ADDR = "3N6S9PLVizPuf8nZkhVzp11PKhTiuTVE6R"

def save_data(data, label):
    with open("data/%s.json" % label, "w") as jsonfile:
        json.dump(data, jsonfile, indent=4, sort_keys=True)
    with open("data/%s.csv" % label, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["bitcoin address",
                         "email",
                         "amount (btc)",
                         "time",
                         "full name",
                         "first name"])
        for d in data:
            writer.writerow([d["addr"],
                             d["email"],
                             d["amount"],
                             d["time"],
                             d["fullname"],
                             d["firstname"]])

def get_address_txs(addr, count=0, stored=None):
    if stored is None:
        response = requests.get(API + addr + "?filter=2")
        if response.status_code == 200:
            return response.json()
        if count < 5:
            print "Request failed, retrying..."
            return get_address_txs(addr, count=count+1)
        print "Request failed."
        return None
    if addr in stored:
        return stored[addr][0]
    return None

def bonus_category(saledata, est, buy):

    # late buyers
    if est.month >= 10 and (est.day > 1 or (est.day == 1 and est.hour >= 12)):
        buy["bonus"] = "0"
        buy["adjusted_amount"] = "0"
        buy["amount"] = str(buy["amount"])
        saledata["late"].append(buy)

    # 0% bonus: Sep 5th - Oct 1st, 12:00pm (EST)
    elif est.month == 10 or (est.month == 9 and (est.day > 5 or (est.day == 5 and est.hour >= 12))):
        buy["bonus"] = "0"
        buy["adjusted_amount"] = str(buy["amount"])
        buy["amount"] = str(buy["amount"])
        saledata["zero"].append(buy)

    # 5% bonus: Aug 27th - Sep 5th, 12:00pm (EST)
    elif est.month == 9 or (est.month == 8 and (est.day > 27 or (est.day == 27 and est.hour >= 12))):
        buy["bonus"] = buy["amount"] * Decimal("0.05")
        buy["adjusted_amount"] = str(buy["amount"] + buy["bonus"])
        buy["bonus"] = str(buy["bonus"])
        buy["amount"] = str(buy["amount"])
        saledata["five"].append(buy)

    # 10% bonus: Aug 22nd -  Aug 27th, 12:00pm (EST)
    elif est.month == 8 and (est.day > 22 or (est.day == 22 and est.hour >= 12)):
        buy["bonus"] = buy["amount"] * Decimal("0.10")
        buy["adjusted_amount"] = str(buy["amount"] + buy["bonus"])
        buy["bonus"] = str(buy["bonus"])
        buy["amount"] = str(buy["amount"])
        saledata["ten"].append(buy)

    # 15% bonus: Aug 17nd to Aug 22nd, 12:00pm (EST)
    else:
        buy["bonus"] = buy["amount"] * Decimal("0.15")
        buy["adjusted_amount"] = str(buy["amount"] + buy["bonus"])
        buy["bonus"] = str(buy["bonus"])
        buy["amount"] = str(buy["amount"])
        saledata["fifteen"].append(buy)

    return saledata

def parse_tx(saledata, user, tx):
    est = datetime.datetime.utcfromtimestamp(tx["time"]) - datetime.timedelta(hours=4)
    for output in tx["out"]:
        if "addr" in output and output["addr"] == user["bitcoin_address"]:
            saledata = bonus_category(saledata, est, {
                "time": str(est),
                "email": user["email"],
                "fullname": user["fullname"].encode("utf8"),
                "firstname": user["firstname"].encode("utf8"),
                "addr": user["bitcoin_address"],
                "amount": Decimal(output["value"]) / Decimal(10**8),
                "timestamp": tx["time"],
                "referral": user["person_who_referred"],
                "accountID": user["data_href"].split('/')[-2]
            })
    return saledata

def get_stormpath_userdata():
    with open("secret.json") as secretfile:
        SECRETS = json.load(secretfile)
    
    ACCOUNTS_API = "https://api.stormpath.com/v1/applications/62cfhD5ihSuFHvjaZ1DxI3/accounts?"
    AUTH = (SECRETS["stormpathid"], SECRETS["stormpathsecret"])

    res = requests.get(ACCOUNTS_API + "limit=1", auth=AUTH)
    num_accounts = res.json()["size"]
    print num_accounts, "accounts found"

    users = {}
    count = 0
    offset = 0
    while offset < num_accounts + 1:
        print offset
        res = requests.get("%soffset=%i&limit=100" % (ACCOUNTS_API, offset), auth=AUTH).json()
        for user in res["items"]:
            count += 1
            customdata = requests.get(user["customData"]["href"], auth=AUTH).json()
            if customdata and "btcAddress" in customdata:
                users[customdata["btcAddress"]] = {
                    "email": user["email"] if "email" in user else 0,
                    "fullname": user["fullName"] if "fullName" in user else 0,
                    "firstname": user["givenName"] if "givenName" in user else 0,
                    "bitcoin_address": customdata["btcAddress"] if "btcAddress" in customdata else 0,
                    "bitcoin_balance": customdata["balance"] if "balance" in customdata else 0,
                    "rep_percent": customdata["repPercentage"] if "repPercentage" in customdata else 0,
                    "referral": customdata["referralCode"] if "referralCode" in customdata else 0,
                    "buyin_ethereum_address": customdata["buyinEthereumAddress"] if "buyinEthereumAddress" in customdata else 0,
                    "ethereum_address": customdata["ethereumAddress"] if "ethereumAddress" in customdata else 0,
                    "data_href": customdata["href"] if "href" in customdata else 0,
                    "person_who_referred": customdata["personWhoReferred"] if "personWhoReferred" in customdata else 0
                }
        offset += 100

    print "Got", len(users.keys()), "users"
    print "count:", count

    with open("data/stormpath_users.json", "w+") as spfile:
        json.dump(users, spfile)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        short_opts = 'hts'
        long_opts = ['help', 'txs', 'stormpath']
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2

    stored = None

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            return 0
        elif opt in ('-t', '--txs'):
            with open("data/alltxs.json") as txfile:
                stored = json.load(txfile)
        elif opt in ('-s', '--stormpath'):
            get_stormpath_userdata()
            return 0

    alltxs = {}
    saledata = { "late": [], "zero": [], "five": [], "ten": [], "fifteen": [] }

    with open("data/stormpath_users.json") as spfile:
        users = json.load(spfile)

    for addr, user in users.items():
        txinfo = get_address_txs(user["bitcoin_address"], stored=stored)
        if txinfo is not None:
            if user["bitcoin_address"] in alltxs:
                alltxs[user["bitcoin_address"]].append(txinfo)
            else:
                alltxs[user["bitcoin_address"]] = [txinfo]
            for tx in txinfo["txs"]:
                saledata = parse_tx(saledata, user, tx)

    # save transactions to file
    with open("data/alltxs.json", "w") as txfile:
        json.dump(alltxs, txfile)

    # save data to file
    for k in saledata:
        save_data(saledata[k], k)

if __name__ == "__main__":
    sys.exit(main())
