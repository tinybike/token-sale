#!/usr/bin/env node

'use strict';

var assert = require('assert');
var augur = require('augur.js');
var log = console.log;

augur.options.BigNumberOnly = false;
augur.connect();

function parseBigNum(n) {
    if (n !== undefined && n !== null && !n.error) {
        return augur.numeric.bignum(n).toNumber();
    }
}

function runtests(ethSaleAddress) {

    var amountToBuy = augur.numeric.bignum(10).toPower(18).toNumber();
    var blockNumber = augur.blockNumber();
    
    var tx = {
        buyRep: {
            method: 'buyRep',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            send: true
        },
        getAmountSent: {
            method: 'getAmountSent',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        getBlockNumSent: {
            method: 'getBlockNumSent',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        getFunderNum: {
            method: 'getFunderNum',
            to: ethSaleAddress,
            from: augur.coinbase
        },
        getAmtByIndex: {
            method: 'getAmtByIndex',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        getAddrByIndex: {
            method: 'getAddrByIndex',
            returns: 'address',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        getBlockNumByIndex: {
            method: 'getBlockNumByIndex',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        addrToFunder: {
            method: 'addrToFunder',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase,
            signature: 'i'
        },
        getFundsRaised: {
            method: 'getFundsRaised',
            returns: 'number',
            to: ethSaleAddress,
            from: augur.coinbase
        }
    };

    log("Initial balance:", augur.fire(tx.getFundsRaised));
    log("Buying:", amountToBuy);

    tx.buyRep.value = amountToBuy;
    augur.transact(tx.buyRep,

        // sent
        function (res) {
            assert(res.txHash !== undefined);
            assert(res.callReturn === '1');
        },

        // success
        function (res) {
            assert(res.txHash !== undefined);
            assert(res.callReturn === '1');
            assert(res.blockHash);
            assert(res.blockNumber);

            var funderNum = parseBigNum(augur.fire(tx.getFunderNum));
            log("Funders:", funderNum);
            
            tx.getAmountSent.params = [augur.coinbase];
            tx.addrToFunder.params = [augur.coinbase];
            tx.getBlockNumSent.params = [augur.coinbase];

            var addrToFunder = augur.fire(tx.addrToFunder);
            log("Funder:", addrToFunder);

            tx.getAmtByIndex.params = [addrToFunder];
            tx.getAddrByIndex.params = [addrToFunder];
            tx.getBlockNumByIndex.params = [addrToFunder];

            var sender = augur.fire(tx.getAddrByIndex);
            log("Sender:", sender);

            var fundsRaised = (augur.fire(tx.getFundsRaised));
            log("Funds raised:", fundsRaised);

            var amountSent = (augur.fire(tx.getAmountSent));
            log("Amount sent:", amountSent);

            var amtByIndex = (augur.fire(tx.getAmtByIndex));
            log("Amount sent (by index):", amtByIndex);

            var blockNumSent = augur.fire(tx.getBlockNumSent);
            log("Blocknumber:", blockNumSent);

            var blockNumByIndex = (augur.fire(tx.getBlockNumByIndex));
            log("Blocknumber (by index):", blockNumByIndex);

            assert(parseBigNum(res.value) === parseBigNum(amountToBuy));
            assert(sender === augur.coinbase);
            assert(parseBigNum(amtByIndex) === amountToBuy);
            assert(parseBigNum(blockNumSent) >= blockNumber);
            assert(parseBigNum(blockNumByIndex) === parseBigNum(blockNumSent));
            assert(parseBigNum(addrToFunder) === parseBigNum(funderNum) - 1);
        },

        // failed
        function (res) {
            res.name = res.error; throw res;
        }
    );
}

runtests(process.argv[2]);
