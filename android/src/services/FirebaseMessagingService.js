/**
 * ECHO OS Android Companion — FCM Service Handler
 * Listens for FCM push notifications from ECHO OS backend and triggers phone actions.
 */

import messaging from '@react-native-firebase/messaging';
import { initiateCall } from './CallManager';
import { sendSmsMessage } from './SmsManager';

export function setupFcmListeners(onLog) {
  // Foreground message handler
  const unsubscribe = messaging().onMessage(async (remoteMessage) => {
    onLog?.(`Received command: ${remoteMessage.data?.command}`);
    handleCommand(remoteMessage.data);
  });

  // Background message handler
  messaging().setBackgroundMessageHandler(async (remoteMessage) => {
    handleCommand(remoteMessage.data);
  });

  return unsubscribe;
}

async function handleCommand(data) {
  if (!data || !data.command) return;

  const { command, payload } = data;
  let parsedPayload = {};
  try {
    parsedPayload = typeof payload === 'string' ? JSON.parse(payload) : payload;
  } catch {}

  switch (command) {
    case 'call':
      if (parsedPayload.phone_number) {
        initiateCall(parsedPayload.phone_number);
      }
      break;

    case 'sms':
      if (parsedPayload.phone_number && parsedPayload.message) {
        sendSmsMessage(parsedPayload.phone_number, parsedPayload.message);
      }
      break;

    case 'ping':
      console.log('ECHO OS Companion ping received');
      break;

    default:
      console.log(`Unknown command: ${command}`);
  }
}
