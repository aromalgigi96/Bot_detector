-- infra/nginx/lua/extract.lua
ngx.log(ngx.ERR, "=====> EXTRACT.LUA FIRED!")

local cjson = require "cjson"
local ok, kafka_produce = pcall(require, "resty.kafka.produce")
if not ok then
    ngx.log(ngx.ERR, "Lua Kafka module not found: ", kafka_produce)
else
    -- initialize with broker list
    local producer, err = kafka_produce.new{
        broker_list = {
            { host = "kafka", port = 9092 }
        }
    }
    if not producer then
        ngx.log(ngx.ERR, "failed to init Kafka producer: ", err)
    else
        -- send your message
        local msg = cjson.encode({
            client_ip = ngx.var.remote_addr,
            method    = ngx.var.request_method,
            uri       = ngx.var.request_uri,
            timestamp = ngx.now(),
        })
        local ok2, err2 = producer:add(msg)
        if not ok2 then
            ngx.log(ngx.ERR, "failed to add Kafka msg: ", err2)
        end
        -- note: you may need to run the background worker if you want async delivery:
        -- require("resty.kafka.produce").worker{
        --   shm_name = "kafka_queue",
        --   producer_config = { broker_list = { { host = "kafka", port = 9092 } } }
        -- }
    end
end
-- always let the request continue
