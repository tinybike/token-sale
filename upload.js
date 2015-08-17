#!/usr/bin/env node

'use strict';

var assert = require('assert');
var execSync = require('child_process').execSync;
var augur = require('augur.js');
var log = console.log;

augur.options.BigNumberOnly = false;
augur.connect();

log("Compile contract");
var ethSaleCompiled = execSync('serpent compile AugurSale.se.py3').toString().trim();

log("Upload contract");
augur.publish(ethSaleCompiled, function (txhash) {
    assert(!txhash.error);
    assert(txhash !== undefined);

    // get transaction receipt
    var getReceipt = function (txhash) {
        var receipt = augur.receipt(txhash);

        // got receipt!
        if (receipt && receipt.contractAddress) {
            log("\nContract address:", receipt.contractAddress);

        // no receipt yet, keep trying...
        } else {
            process.stdout.write(".");
            setTimeout(function () { getReceipt(txhash); }, 6000);
        }

    };

    process.stdout.write("Wait for receipt");
    getReceipt(txhash);

});
