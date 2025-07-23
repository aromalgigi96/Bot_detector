# infra/nginx/Dockerfile
FROM openresty/openresty:1.21.4.1-4-alpine

# install build tools + luarocks
RUN apk add --no-cache build-base openssl-dev luarocks \
  && luarocks install lua-resty-kafka \
  && apk del build-base openssl-dev luarocks

# copy your config + lua
COPY nginx.conf /etc/nginx/nginx.conf
COPY lua/extract.lua /etc/nginx/extract.lua
