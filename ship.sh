#! /bin/bash

rm -rf upload
mkdir upload
cp -r config upload
cp -r consts upload
cp -r handler upload
cp -r util upload
cp *.py upload
scp -r ./upload/* wechat@newbuy-prod-pay01:/home/wechat/service
