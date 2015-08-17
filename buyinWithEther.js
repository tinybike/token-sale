#!/usr/bin/env node

'use strict';

var web3 = require('web3');
var eth = web3.eth;
var log = console.log;

web3.setProvider(new web3.providers.HttpProvider('http://localhost:8545'));

function buyin(contractAddress) {

    var MyContract = eth.contract([{
        "name": "addrToFunder(int256)",
        "type": "function",
        "inputs": [{ "name": "address", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "buyRep()",
        "type": "function",
        "inputs": [],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getAddrByIndex(int256)",
        "type": "function",
        "inputs": [{ "name": "index", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getAmountSent(int256)",
        "type": "function",
        "inputs": [{ "name": "address", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getAmtByIndex(int256)",
        "type": "function",
        "inputs": [{ "name": "index", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getBlockNumByIndex(int256)",
        "type": "function",
        "inputs": [{ "name": "index", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getBlockNumSent(int256)",
        "type": "function",
        "inputs": [{ "name": "address", "type": "int256" }],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getFunderNum()",
        "type": "function",
        "inputs": [],
        "outputs": [{ "name": "out", "type": "int256" }]
    },
    {
        "name": "getFundsRaised()",
        "type": "function",
        "inputs": [],
        "outputs": [{ "name": "out", "type": "int256" }]
    }]);

    var sale = MyContract.at(contractAddress);

    log("Buy in from:", eth.coinbase);

    var txhash = sale.buyRep({
        from: eth.coinbase,
        value: web3.toWei(1, "ether"),
        gas: 150000
    });

    log("txHash:", txhash);

    setTimeout(function () {

        var amountSent = web3.fromWei(
            sale.getAmountSent.call(eth.coinbase),
            "ether"
        ).toFixed();

        log("amountSent:", amountSent);

        process.exit(0);

    }, 30000);

}

buyin(process.argv[2]);
