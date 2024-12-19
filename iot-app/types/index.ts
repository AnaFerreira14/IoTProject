export const STORAGE_KEYS = {
  IDENTITY_POOL_ID: "@aws_identity_pool_id",
  MQTT_ENDPOINT: "@aws_mqtt_endpoint",
  REGION: "@aws_region",
  TOPIC: "@aws_topic",
};

export interface SensorReading {
  id: string;
  temperature: number;
  pressure: number;
  light: number;
  timestamp: string;
}

export interface AwsConfig {
  identityPoolId: string;
  mqttEndpoint: string;
  region: string;
  topic: string;
}
