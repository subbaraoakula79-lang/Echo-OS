/**
 * ECHO OS Android Companion — Call Manager
 * Launches the native Android phone dialer or directly places a phone call.
 */

import { Linking, PermissionsAndroid, Platform } from 'react-native';

export async function initiateCall(phoneNumber) {
  const formattedNumber = phoneNumber.replace(/[^0-9+]/g, '');

  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.CALL_PHONE,
        {
          title: 'ECHO OS Phone Permission',
          message: 'ECHO OS requires access to make phone calls requested by your AI assistant.',
          buttonPositive: 'Allow',
        }
      );

      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        Linking.openURL(`tel:${formattedNumber}`);
      } else {
        // Fallback to dialer prompt
        Linking.openURL(`tel:${formattedNumber}`);
      }
    } catch (err) {
      Linking.openURL(`tel:${formattedNumber}`);
    }
  } else {
    Linking.openURL(`tel:${formattedNumber}`);
  }
}
