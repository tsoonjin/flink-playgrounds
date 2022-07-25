CREATE TABLE user_logs_kafka (
  `ts` TIMESTAMP(3),
  `msg` STRING,
  WATERMARK FOR `ts` AS `ts` - INTERVAL '10' SECOND
) WITH (
  'connector.type' = 'kafka',       
  'connector.version' = 'universal',
  'connector.topic' = 'user-logs',
  'connector.properties.zookeeper.connect' = 'not-needed',
  'connector.properties.bootstrap.servers' = 'kafka:9092',
  'connector.startup-mode' = 'earliest-offset',
  'format.type' = 'json'
);
