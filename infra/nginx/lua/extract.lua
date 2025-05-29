local cjson = require "cjson"

-- Try to load the Kafka producer module
local ok, producer_mod = pcall(require, "resty.kafka.producer")
if not ok then
    ngx.log(ngx.ERR, "Lua Kafka module not found: ", producer_mod)
else
    -- Safely initialize the producer
    local bp, err = producer_mod:new({ hosts = { "kafka:9092" } })
    if not bp then
        ngx.log(ngx.ERR, "failed to init Kafka producer: ", err)
    else
        -- Build and send the event message
        local msg = {
            client_ip = ngx.var.remote_addr,
            method    = ngx.var.request_method,
            uri       = ngx.var.request_uri,
            timestamp = ngx.now()
        }
        local ok, err = bp:send("raw-events", nil, cjson.encode(msg))
        if not ok then
            ngx.log(ngx.ERR, "failed to send to Kafka: ", err)
        end
    end
end

-- Always continue and proxy the request
-- (this makes sure NGINX returns your backend’s response instead of 500)
