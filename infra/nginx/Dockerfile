# infra/nginx/Dockerfile

FROM openresty/openresty:alpine

# 1) Install the tools OPM needs
RUN apk add --no-cache curl bash perl

# 2) Use OPM to fetch a maintained lua-resty-kafka client
RUN /usr/local/openresty/bin/opm get doujiang24/lua-resty-kafka

# 3) Copy in your NGINX config & Lua scripts
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY lua/           /usr/local/openresty/nginx/lua/
