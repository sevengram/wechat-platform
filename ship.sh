#! /bin/bash

cp -r config upload
cp -r consts upload
cp -r handler upload
cp -r sql upload
cp -r util upload
cp *.py upload 
scp -r ./upload/* wechat@newbuy-qa-pay01:/home/wechat/service
