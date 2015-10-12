#!/usr/bin/env node
/**
 * Augur token sale Ether results.
 * @author Jack Peterson (jack@tinybike.net)
 */

"use strict";

var fs = require("fs");
var path = require("path");
var _ = require("lodash");
var async = require("async");
var moment = require("moment");
var ethrpc = require("ethrpc");
var abi = require("augur-abi");
var usersBtcIndex = require("./data/stormpath_users");

var users = {};
for (var user in usersBtcIndex) {
    if (!usersBtcIndex.hasOwnProperty(user)) continue;
    if (usersBtcIndex[user].buyin_ethereum_address) {
        if (usersBtcIndex[user].buyin_ethereum_address.constructor === Array) {
            for (var i = 0, len = usersBtcIndex[user].buyin_ethereum_address.length; i < len; ++i) {
                users[usersBtcIndex[user].buyin_ethereum_address[i].replace("0x", "")] = usersBtcIndex[user];
            }
        } else {
            users[usersBtcIndex[user].buyin_ethereum_address] = usersBtcIndex[user];
        }
    }
}

ethrpc.nodes.local = "http://eth2.augur.net";
ethrpc.balancer = false;
ethrpc.excision = false;

var coinbase = ethrpc.coinbase();
var ethSaleAddress = "0xe28e72fcf78647adce1f1252f240bbfaebd63bcc";
var tx = {
    buyRep: {
        method: "buyRep",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        send: true
    },
    getAmountSent: {
        method: "getAmountSent",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    getBlockNumSent: {
        method: "getBlockNumSent",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    getFunderNum: {
        method: "getFunderNum",
        to: ethSaleAddress,
        from: coinbase
    },
    getAmtByIndex: {
        method: "getAmtByIndex",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    getAddrByIndex: {
        method: "getAddrByIndex",
        returns: "address",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    getBlockNumByIndex: {
        method: "getBlockNumByIndex",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    addrToFunder: {
        method: "addrToFunder",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase,
        signature: "i"
    },
    getFundsRaised: {
        method: "getFundsRaised",
        returns: "number",
        to: ethSaleAddress,
        from: coinbase
    }
};

var buys = {};

ethrpc.blockNumber(function (blockNumber) {
    blockNumber = parseInt(blockNumber);
    ethrpc.fire(tx.getFunderNum, function (numFunders) {
        numFunders = parseInt(numFunders);
        async.eachSeries(_.range(0, numFunders), function (funder, nextFunder) {
            var buy = {};
            tx.getAmtByIndex.params = funder;
            ethrpc.fire(tx.getAmtByIndex, function (amount) {
                if (amount) {
                    buy.index = funder;
                    buy.amount = abi.bignum(amount).dividedBy(ethrpc.ETHER).toFixed();
                    tx.getAddrByIndex.params = funder;
                    return ethrpc.fire(tx.getAddrByIndex, function (address) {
                        if (address) {
                            buy.address = address;
                            tx.getBlockNumByIndex.params = funder;
                            return ethrpc.fire(tx.getBlockNumByIndex, function (blockNumSent) {
                                if (blockNumSent && parseInt(blockNumSent)) {
                                    buy.blocknumber = parseInt(blockNumSent);
                                    return ethrpc.getBlockByNumber(buy.blocknumber, true, function (block) {
                                        if (block && block.timestamp) {

                                            // late buyers
                                            if (buy.blocknumber >= 317594) {
                                                buy.group = "late";
                                                buy.bonus = 0;
                                                buy.adjusted_amount = buy.amount;

                                            // 0% bonus
                                            } else if (buy.blocknumber >= 188576) {
                                                buy.group = "0%";
                                                buy.bonus = 0;
                                                buy.adjusted_amount =  buy.amount;

                                            // 5% bonus
                                            } else if (buy.blocknumber >= 151173) {
                                                buy.group = "5%";
                                                buy.bonus = abi.bignum(buy.amount).times(abi.bignum("0.05"));
                                                buy.adjusted_amount = abi.bignum(buy.amount).plus(buy.bonus).toFixed();
                                                buy.bonus = buy.bonus.toFixed();

                                            // 10% bonus
                                            } else if (buy.blocknumber >= 125987) {
                                                buy.group = "10%";
                                                buy.bonus = abi.bignum(buy.amount).times(abi.bignum("0.1"));
                                                buy.adjusted_amount = abi.bignum(buy.amount).plus(buy.bonus).toFixed();
                                                buy.bonus = buy.bonus.toFixed();

                                            // 15% bonus
                                            } else {
                                                buy.group = "15%";
                                                buy.bonus = abi.bignum(buy.amount).times(abi.bignum("0.15"));
                                                buy.adjusted_amount = abi.bignum(buy.amount).plus(buy.bonus).toFixed();
                                                buy.bonus = buy.bonus.toFixed();
                                            }

                                            buy.timestamp = parseInt(block.timestamp);

                                            var user = users[address.replace("0x", "")];
                                            if (user && user.email) {
                                                buy.email = user.email;
                                                buy.referral = user.referral;
                                            } else {
                                                buy.email = null;
                                                buy.referral = null;
                                            }

                                            console.log(
                                                funder.toString(), "\t",
                                                buy.address, "\t",
                                                buy.blocknumber, "\t",
                                                buy.timestamp, "\t",
                                                buy.group, "\t",
                                                buy.amount, "\t",
                                                buy.email, "\t",
                                                buy.referral
                                            );

                                            if (buys[address]) {
                                                buys[address].push(buy);
                                            } else {
                                                buys[address] = [buy];
                                            }
                                            return nextFunder();
                                        } else {
                                            nextFunder("couldn't get block: " + JSON.stringify(block, null, 2));
                                        }
                                    });
                                }
                                nextFunder("couldn't get blocknumber: " + blockNumSent.toString());
                            });
                        }
                        nextFunder("couldn't get address: " + address.toString());
                    });
                }
                nextFunder("couldn't get amount:" + amount.toString());
            });
        }, function (err) {
            if (err) return console.error("[async.each]", err);
            fs.writeFile("data/eth-buys.json", JSON.stringify(buys, null, 4), function (err) {
                if (err) return console.error("[fs.writeFile]", err);
                console.log("Wrote results to file successfully");
            });
        });
    });
});
