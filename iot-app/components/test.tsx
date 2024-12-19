// App.tsx
import { Amplify } from "aws-amplify";

import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";
import { PubSub } from "@aws-amplify/pubsub";
import { CONNECTION_STATE_CHANGE, ConnectionState } from "@aws-amplify/pubsub";
import { Hub } from "aws-amplify/utils";

Hub.listen("pubsub", (data: any) => {
  const { payload } = data;
  if (payload.event === CONNECTION_STATE_CHANGE) {
    const connectionState = payload.data.connectionState as ConnectionState;
    console.log(connectionState);
  }
});

Amplify.configure({
  Auth: {
    Cognito: {
      identityPoolId: "eu-north-1:663c2474-9f4f-4019-8e7c-eea85fb6e754",
      allowGuestAccess: true,
    },
  },
});

interface PubSubSubscription {
  unsubscribe: () => void;
}

export default function IoTMonitor(): JSX.Element {
  const [sensorData, setSensorData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let subscription: PubSubSubscription;

    const setupIoTSubscription = async (): Promise<void> => {
      try {
        // Subscribe to an IoT topic
        const pubsub = new PubSub({
          region: "eu-north-1",
          endpoint:
            "wss://a2hako4exonbcq-ats.iot.eu-north-1.amazonaws.com/mqtt",
        });

        subscription = pubsub
          .subscribe({ topics: "sensor_readings" })
          .subscribe({
            next: (data) => {
              console.log("Message received:", data);
              setSensorData((prevData) => [...prevData, data]);
            },
            error: (err: Error) => {
              console.error("Subscription error:", err);
              setError(err.message);
            },
            complete: () => {
              console.log("Subscription complete");
            },
          });
        console.log("setup pub sub");
      } catch (err) {
        console.error("Error setting up subscription:", err);
        setError(err instanceof Error ? err.message : "Unknown error occurred");
      }
    };

    setupIoTSubscription();

    // Cleanup subscription on component unmount
    return () => {
      if (subscription) {
        subscription.unsubscribe();
      }
    };
  }, []);

  return (
    <View style={styles.container}>
      {error ? (
        <Text style={styles.error}>Error: {error}</Text>
      ) : (
        <>
          <Text style={styles.title}>IoT Sensor Data</Text>
          <Text style={styles.data}>
            {sensorData
              ? JSON.stringify(sensorData, null, 2)
              : "Waiting for data..."}
          </Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  data: {
    fontSize: 16,
    marginBottom: 10,
  },
  error: {
    color: "red",
    fontSize: 16,
  },
});
