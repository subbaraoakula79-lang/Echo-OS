/**
 * ECHO OS Android Companion — SMS Manager
 * Sends SMS messages directly or opens SMS composer.
 */

import { Linking, PermissionsAndroid, Platform } from 'react-native';

export async function sendSmsMessage(phoneNumber, message) {
  const formattedNumber = phoneNumber.replace(/[^0-9+]/g, '');

  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.SEND_SMS,
        {
          title: 'ECHO OS SMS Permission',
          message: 'ECHO OS requires access to send text messages requested by your AI assistant.',
          buttonPositive: 'Allow',
        }
      );

      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        const separator = Platform.OS === 'ios' ? '&' : '?';
        Linking.openURL(`sms:${formattedNumber}${separator}body=${encodeURIComponent(message)}`);
      } else {
        Linking.openURL(`sms:${formattedNumber}?body=${encodeURIComponent(message)}`);
      }
    } catch {
      Linking.openURL(`sms:${formattedNumber}?body=${encodeURIComponent(message)}`);
    }
  }
}
