// app/index.tsx
import React, { useState, useEffect, useCallback } from "react";
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Feather } from "@expo/vector-icons";
import { PubSub } from "@aws-amplify/pubsub";
import { CONNECTION_STATE_CHANGE, ConnectionState } from "@aws-amplify/pubsub";
import { Hub } from "aws-amplify/utils";
import { Amplify } from "aws-amplify";
import { useSettings } from "@/context/SettingsContext";
import { SensorReading } from "@/types";
import { Colors } from "@/constants/Colors";

// Listen for connection state changes
Hub.listen(
  "pubsub",
  (data: {
    payload: { event: string; data: { connectionState: ConnectionState } };
  }) => {
    const { payload } = data;
    if (payload.event === CONNECTION_STATE_CHANGE) {
      console.log("Connection state:", payload.data.connectionState);
    }
  }
);

export default function HomeScreen(): JSX.Element {
  const { config, error: configError, version } = useSettings();
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [subscription, setSubscription] = useState<
    { unsubscribe: () => void } | undefined
  >();

  // Configure Amplify whenever config changes
  useEffect(() => {
    if (config?.identityPoolId) {
      Amplify.configure({
        Auth: {
          Cognito: {
            identityPoolId: config.identityPoolId,
            allowGuestAccess: true,
          },
        },
      });
    }
  }, [config?.identityPoolId]);

  // Cleanup function for PubSub subscription
  const cleanupSubscription = useCallback(() => {
    if (subscription) {
      subscription.unsubscribe();
      setSubscription(undefined);
    }
  }, [subscription]);

  // Set up PubSub subscription
  useEffect(() => {
    let isMounted = true;
    let subscription: { unsubscribe: () => void } | undefined;

    const setupIoTSubscription = async () => {
      if (!config || !isMounted) return;

      try {
        setIsConnecting(true);

        const pubsub = new PubSub({
          region: config.region,
          endpoint: config.mqttEndpoint,
        });

        subscription = pubsub.subscribe({ topics: [config.topic] }).subscribe({
          next: (data: any) => {
            if (!isMounted) return;
            console.log("Message received:", data);

            const formattedReading: SensorReading = {
              id: Date.now().toString(),
              temperature: data?.temperature ?? 0,
              pressure: data?.humidity ?? 0,
              light: data?.light ?? 0,
              timestamp: new Date(
                data?.time_stamp || new Date()
              ).toLocaleString(),
            };

            setReadings((prevReadings) =>
              [formattedReading, ...prevReadings].slice(0, 21)
            );
          },
          error: (err: Error) => {
            if (!isMounted) return;
            console.error("Subscription error:", err);
            setError(err.message);
            setIsConnecting(false);
          },
          complete: () => {
            if (!isMounted) return;
            console.log("Subscription complete");
            setIsConnecting(false);
          },
        });

        if (isMounted) {
          setIsConnecting(false);
          setError(null);
        }
      } catch (err) {
        if (!isMounted) return;
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error occurred";
        console.error("Error setting up subscription:", err);
        setError(errorMessage);
        setIsConnecting(false);
      }
    };

    setupIoTSubscription();

    return () => {
      isMounted = false;
      if (subscription) {
        subscription.unsubscribe();
      }
    };
  }, [config, version]);

  const latestReading: SensorReading = readings[0] || {
    id: "0",
    temperature: 0,
    pressure: 0,
    light: 0,
    timestamp: "No data yet",
  };

  if (!config) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Please configure AWS settings</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.scrollView}>
      {/* App Name and Status */}
      <View style={styles.appNameContainer}>
        <Text style={styles.appName}>IoT Project 2024</Text>
        {isConnecting && (
          <View style={styles.connectingContainer}>
            <ActivityIndicator color={Colors.light.tint} />
            <Text style={styles.connectingText}>Connecting to AWS IoT...</Text>
          </View>
        )}
        {(error || configError) && (
          <Text style={styles.errorText}>Error: {error || configError}</Text>
        )}
      </View>

      {/* Main Card with Latest Readings */}
      <View style={styles.mainCardContainer}>
        <LinearGradient colors={["#4568DC", "#B06AB3"]} style={styles.mainCard}>
          <View style={styles.mainCardHeader}>
            <Text style={styles.mainCardTitle}>Current Readings</Text>
            <Text style={styles.mainCardTimestamp}>
              {latestReading.timestamp}
            </Text>
          </View>

          <View style={styles.readingsContainer}>
            <View style={styles.readingItem}>
              <Feather name="thermometer" size={24} color="white" />
              <Text style={styles.readingValue}>
                {latestReading.temperature.toFixed(1)}°C
              </Text>
              <Text style={styles.readingLabel}>Temperature</Text>
            </View>

            <View style={styles.readingItem}>
              <Feather name="cloud" size={24} color="white" />
              <Text style={styles.readingValue}>
                {latestReading.pressure.toFixed(1)} %
              </Text>
              <Text style={styles.readingLabel}>Humidity</Text>
            </View>

            <View style={styles.readingItem}>
              <Feather name="sun" size={24} color="white" />
              <Text style={styles.readingValue}>
                {latestReading.light.toFixed(0)} lux
              </Text>
              <Text style={styles.readingLabel}>Light</Text>
            </View>
          </View>
        </LinearGradient>
      </View>

      {/* Historical Readings List */}
      <View style={styles.historicalReadingsContainer}>
        <Text style={styles.historicalReadingsTitle}>Previous Readings</Text>
        {readings.slice(1).map((reading) => (
          <View key={reading.id} style={styles.historicalReadingItem}>
            <View style={styles.historicalReadingTimestampContainer}>
              <Text style={styles.historicalReadingTimestamp}>
                {reading.timestamp}
              </Text>
            </View>
            <View style={styles.historicalReadingValuesContainer}>
              <View style={styles.historicalReadingValueItem}>
                <Text style={styles.historicalReadingValueIcon}>🌡️</Text>
                <Text style={styles.historicalReadingValue}>
                  {reading.temperature.toFixed(1)}°C
                </Text>
              </View>
              <View style={styles.historicalReadingValueItem}>
                <Text style={styles.historicalReadingValueIcon}>🌬️</Text>
                <Text style={styles.historicalReadingValue}>
                  {reading.pressure.toFixed(1)} %
                </Text>
              </View>
              <View style={styles.historicalReadingValueItem}>
                <Text style={styles.historicalReadingValueIcon}>☀️</Text>
                <Text style={styles.historicalReadingValue}>
                  {reading.light.toFixed(0)} lux
                </Text>
              </View>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
    backgroundColor: "#F4F7F6",
  },
  centerContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  connectingContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 5,
  },
  connectingText: {
    marginLeft: 10,
    color: Colors.light.tint,
  },
  appNameContainer: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
  },
  appName: {
    fontSize: 24,
    fontWeight: "700",
    color: "#2C3E50",
  },
  errorText: {
    color: "red",
    marginTop: 5,
  },
  mainCardContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  mainCard: {
    borderRadius: 20,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  mainCardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 15,
  },
  mainCardTitle: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
  },
  mainCardTimestamp: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 14,
  },
  readingsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 10,
  },
  readingItem: {
    alignItems: "center",
    flex: 1,
  },
  readingValue: {
    color: "white",
    fontSize: 20,
    fontWeight: "700",
    marginTop: 5,
  },
  readingLabel: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 12,
    marginTop: 5,
  },
  historicalReadingsContainer: {
    paddingHorizontal: 20,
    paddingBottom: 50,
  },
  historicalReadingsTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 15,
    color: "#2C3E50",
  },
  historicalReadingItem: {
    backgroundColor: "white",
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 1,
  },
  historicalReadingTimestampContainer: {
    alignItems: "center",
    marginBottom: 10,
  },
  historicalReadingTimestamp: {
    color: "#7F8C8D",
    fontSize: 12,
  },
  historicalReadingValuesContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  historicalReadingValueItem: {
    flexDirection: "row",
    alignItems: "center",
  },
  historicalReadingValueIcon: {
    marginRight: 5,
    fontSize: 16,
  },
  historicalReadingValue: {
    fontSize: 14,
    color: "#2C3E50",
  },
});
