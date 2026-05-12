import { firebase } from '@nativescript/firebase-core';
import '@nativescript/firebase-messaging';
import { alert, Frame } from '@nativescript/core';
import { usersService } from '~/init/services';

export async function initFirebase() {
  try {
    await firebase();
    const messaging = firebase().messaging();
    const authStatus = await messaging.requestPermission();
    
    if (authStatus === 1 || authStatus === 2) {
      console.log('Notification permission granted');
    } else {
      console.log('Notification permission denied');
    }

    messaging.showNotificationsWhenInForeground = true;

    messaging.onMessage((remoteMessage: any) => {
      console.log('Foreground message:', remoteMessage);
      if (remoteMessage.notification) {
        alert({
          title: remoteMessage.notification.title || 'Уведомление',
          message: remoteMessage.notification.body || '',
          okButtonText: 'OK'
        });
      }
      handleNotificationTap(remoteMessage.data);
    });

    messaging.onNotificationTap((remoteMessage: any) => {
      handleNotificationTap(remoteMessage.data);
    });

    messaging.onToken(async (token: string) => {
      await registerTokenOnServer(token);
    });

    const token = await messaging.getToken();
    if (token) {
      await registerTokenOnServer(token);
    }
  } catch (err) {
    console.error('Firebase init error:', err);
  }
}

async function registerTokenOnServer(token: string) {
  try {
    const { secureStorage } = require('~/init/storage');
    const accessToken = secureStorage.getSync({ key: 'accessToken' });
    if (accessToken) {
      await usersService.registerFcmToken(token);
      console.log('FCM token registered on server');
    } else {
      console.log('User not logged in, skipping token registration');
    }
  } catch (err) {
    console.error('Failed to register FCM token:', err);
  }
}

function handleNotificationTap(data: any) {
  if (data && data.postId) {
    const frame = Frame.topmost();
    if (frame) {
      setTimeout(() => {
        frame.navigate({
          moduleName: '~/components/Recipe',
          context: { postId: data.postId },
          transition: { name: 'slideLeft', duration: 300 }
        });
      }, 100);
    } else {
      console.warn('No topmost frame found - cannot navigate to Recipe');
    }
  }
}

export async function forceRegisterCurrentToken() {
    try {
        const messaging = firebase().messaging();
        const token = await messaging.getToken();
        if (token) {
            await registerTokenOnServer(token);
        }
    } catch (err) {
        console.error('Manual token registration failed:', err);
    }
}
