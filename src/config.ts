import { Device, isAndroid } from '@nativescript/core'

function isEmulator() {
  if (!isAndroid) {
    return false
  }

  const fingerprint = android.os.Build.FINGERPRINT || ''
  const model = android.os.Build.MODEL || ''

  return (
    fingerprint.includes('generic') ||
    fingerprint.includes('emulator') ||
    model.includes('Emulator') ||
    model.includes('Android SDK built for x86')
  )
}

export const API_BASE_URL = isEmulator()
  ? 'http://10.0.2.2:5000'
  : 'http://192.168.0.15:5000'
