import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Dimensions,
  Alert,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import { Colors } from "@/constants/Colors";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useSettings } from "@/context/SettingsContext";

const STORAGE_KEYS = {
  IDENTITY_POOL_ID: "@aws_identity_pool_id",
  MQTT_ENDPOINT: "@aws_mqtt_endpoint",
  REGION: "@aws_region",
  TOPIC: "@aws_topic",
};

export default function Settings() {
  const { config, error: configError, version, saveSettings } = useSettings();
  const [identityPoolId, setIdentityPoolId] = useState("");
  const [mqttEndpoint, setMqttEndpoint] = useState("");
  const [region, setRegion] = useState("");
  const [topic, setTopic] = useState("");

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const storedIdentityPoolId = config?.identityPoolId;
      const storedMqttEndpoint = config?.mqttEndpoint;
      const storedRegion = config?.region;
      const storedTopic = config?.topic;

      if (storedIdentityPoolId) setIdentityPoolId(storedIdentityPoolId);
      if (storedMqttEndpoint) setMqttEndpoint(storedMqttEndpoint);
      if (storedRegion) setRegion(storedRegion);
      if (storedTopic) setTopic(storedTopic);
    } catch (error) {
      Alert.alert("Error", "Failed to load settings");
      console.error("Error loading settings:", error);
    }
  };

  const handleSaveSettings = async () => {
    try {
      await saveSettings({
        identityPoolId,
        mqttEndpoint,
        region,
        topic,
      });
      Alert.alert("Success", "Settings saved successfully");
    } catch (error) {
      Alert.alert("Error", "Failed to save settings");
      console.error("Error saving settings:", error);
    }
  };

  return (
    <ScrollView style={styles.scrollView}>
      <View style={styles.appNameContainer}>
        <Text style={styles.appName}>IoT Project 2024</Text>
        <Text style={styles.pageTitle}>AWS IoT Settings</Text>
      </View>

      <View style={styles.settingsCardContainer}>
        <View style={styles.settingsCard}>
          {/* Identity Pool ID Input */}
          <View style={styles.inputContainer}>
            <Feather
              name="key"
              size={20}
              color={Colors.light.tint}
              style={styles.inputIcon}
            />
            <TextInput
              style={styles.input}
              placeholder="AWS Identity Pool ID"
              value={identityPoolId}
              onChangeText={setIdentityPoolId}
              autoCapitalize="none"
            />
          </View>

          {/* MQTT Endpoint Input */}
          <View style={styles.inputContainer}>
            <Feather
              name="link"
              size={20}
              color={Colors.light.tint}
              style={styles.inputIcon}
            />
            <TextInput
              style={styles.input}
              placeholder="AWS MQTT Endpoint"
              value={mqttEndpoint}
              onChangeText={setMqttEndpoint}
              autoCapitalize="none"
            />
          </View>

          {/* Region Input */}
          <View style={styles.inputContainer}>
            <Feather
              name="globe"
              size={20}
              color={Colors.light.tint}
              style={styles.inputIcon}
            />
            <TextInput
              style={styles.input}
              placeholder="AWS Region"
              value={region}
              onChangeText={setRegion}
              autoCapitalize="none"
            />
          </View>

          {/* Topic Input */}
          <View style={styles.inputContainer}>
            <Feather
              name="message-circle"
              size={20}
              color={Colors.light.tint}
              style={styles.inputIcon}
            />
            <TextInput
              style={styles.input}
              placeholder="MQTT Topic"
              value={topic}
              onChangeText={setTopic}
              autoCapitalize="none"
            />
          </View>

          {/* Save Button */}
          <TouchableOpacity
            style={styles.saveButton}
            onPress={handleSaveSettings}
          >
            <Text style={styles.saveButtonText}>Save Settings</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
    backgroundColor: "#F4F7F6",
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
  pageTitle: {
    fontSize: 16,
    color: "#7F8C8D",
    marginTop: 5,
  },
  settingsCardContainer: {
    paddingHorizontal: 20,
  },
  settingsCard: {
    backgroundColor: "white",
    borderRadius: 20,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 2,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#ECF0F1",
    marginBottom: 15,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    height: 40,
    color: "#2C3E50",
  },
  saveButton: {
    backgroundColor: Colors.light.tint,
    borderRadius: 10,
    paddingVertical: 15,
    alignItems: "center",
    marginTop: 20,
  },
  saveButtonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});
