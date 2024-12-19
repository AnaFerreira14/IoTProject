// context/SettingsContext.tsx
import React, { createContext, useContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Alert } from "react-native";
import { STORAGE_KEYS, AwsConfig } from "@/types";

interface SettingsContextType {
  config: AwsConfig | null;
  error: string | null;
  refreshSettings: () => Promise<void>;
  saveSettings: (newConfig: AwsConfig) => Promise<void>;
  version: number;
}

const SettingsContext = createContext<SettingsContextType | null>(null);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
};

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [config, setConfig] = useState<AwsConfig | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);

  const loadConfig = async (): Promise<void> => {
    try {
      const [identityPoolId, mqttEndpoint, region, topic] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.IDENTITY_POOL_ID),
        AsyncStorage.getItem(STORAGE_KEYS.MQTT_ENDPOINT),
        AsyncStorage.getItem(STORAGE_KEYS.REGION),
        AsyncStorage.getItem(STORAGE_KEYS.TOPIC),
      ]);

      if (!identityPoolId || !mqttEndpoint || !region || !topic) {
        throw new Error("Missing AWS configuration. Please check settings.");
      }

      const newConfig = {
        identityPoolId,
        mqttEndpoint,
        region,
        topic,
      };

      setConfig(newConfig);
      setVersion((v) => v + 1);
      setError(null);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load AWS configuration";
      setError(errorMessage);
      setConfig(null);
    }
  };

  const saveSettings = async (newConfig: AwsConfig): Promise<void> => {
    try {
      await Promise.all([
        AsyncStorage.setItem(
          STORAGE_KEYS.IDENTITY_POOL_ID,
          newConfig.identityPoolId
        ),
        AsyncStorage.setItem(
          STORAGE_KEYS.MQTT_ENDPOINT,
          newConfig.mqttEndpoint
        ),
        AsyncStorage.setItem(STORAGE_KEYS.REGION, newConfig.region),
        AsyncStorage.setItem(STORAGE_KEYS.TOPIC, newConfig.topic),
      ]);

      setConfig(newConfig);
      setVersion((v) => v + 1);
      setError(null);
      Alert.alert("Success", "Settings saved successfully");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save settings";
      setError(errorMessage);
      Alert.alert("Error", errorMessage);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const value = {
    config,
    error,
    refreshSettings: loadConfig,
    saveSettings,
    version,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};
