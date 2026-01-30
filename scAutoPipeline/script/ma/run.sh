#!/bin/bash
docker run   --rm -v /home/chenglong.liu:/home/chenglong.liu -v /nas:/nas crpi-nc6vrpgro1z8mu8m.cn-chengdu.personal.cr.aliyuncs.com/lclimage/music:v1.0.0 \
Rscript /home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/script/ma/ma.r -h


