/**
 * ECHO OS — Android Companion App Interface
 * Shows device registration status, FCM push token, and action logs.
 */

import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import messaging from '@react-native-firebase/messaging';
import { setupFcmListeners } from './src/services/FirebaseMessagingService';

export default function App() {
  const [fcmToken, setFcmToken] = useState('Fetching token...');
  const [logs, setLogs] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Request FCM permission and get token
    async function initFcm() {
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        const token = await messaging().getToken();
        setFcmToken(token);
        setIsConnected(true);
        addLog(`Device registered. Token: ${token.slice(0, 15)}...`);
      } else {
        setFcmToken('Permission denied');
        addLog('FCM permission denied');
      }
    }

    initFcm();

    const unsubscribe = setupFcmListeners((msg) => addLog(msg));
    return unsubscribe;
  }, []);

  function addLog(msg) {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [`[${time}] ${msg}`, ...prev.slice(0, 20)]);
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0a0e15" />
      <View style={styles.header}>
        <Text style={styles.title}>ECHO OS</Text>
        <Text style={styles.subtitle}>ANDROID COMPANION</Text>
        <View style={styles.statusBadge}>
          <View style={[styles.statusDot, { backgroundColor: isConnected ? '#ff5e00' : '#ff0044' }]} />
          <Text style={styles.statusText}>{isConnected ? 'LINKED TO DESKTOP' : 'DISCONNECTED'}</Text>
        </View>
      </View>

      <View style={styles.tokenCard}>
        <Text style={styles.cardTitle}>FCM PUSH TOKEN</Text>
        <Text style={styles.tokenText} numberOfLines={2}>{fcmToken}</Text>
      </View>

      <View style={styles.logContainer}>
        <Text style={styles.cardTitle}>COMMAND LOGS</Text>
        <ScrollView style={styles.logList}>
          {logs.map((log, idx) => (
            <Text key={idx} style={styles.logItem}>{log}</Text>
          ))}
          {logs.length === 0 && (
            <Text style={styles.emptyLog}>Waiting for desktop commands...</Text>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0e15', padding: 20 },
  header: { marginBottom: 20 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#ff5e00', letterSpacing: 4 },
  subtitle: { fontSize: 10, color: 'rgba(255,255,255,0.4)', letterSpacing: 2, marginTop: 2 },
  statusBadge: { flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  statusDot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  statusText: { color: '#ffffff', fontSize: 11, fontWeight: '600', letterSpacing: 1 },
  tokenCard: { backgroundColor: '#0d1117', borderRadius: 8, padding: 15, marginBottom: 20, borderWidth: 1, borderColor: 'rgba(255,94,0,0.15)' },
  cardTitle: { fontSize: 9, color: '#ff5e00', letterSpacing: 2, fontWeight: 'bold', marginBottom: 6 },
  tokenText: { color: 'rgba(255,255,255,0.6)', fontSize: 11, fontFamily: 'monospace' },
  logContainer: { flex: 1, backgroundColor: '#0d1117', borderRadius: 8, padding: 15, borderWidth: 1, borderColor: 'rgba(255,94,0,0.15)' },
  logList: { flex: 1, marginTop: 5 },
  logItem: { color: 'rgba(255,255,255,0.7)', fontSize: 11, fontFamily: 'monospace', marginBottom: 4 },
  emptyLog: { color: 'rgba(255,255,255,0.2)', fontSize: 11, fontStyle: 'italic' },
});
