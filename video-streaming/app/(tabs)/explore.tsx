import React, { useState, useEffect, useRef } from "react";
import { View, StyleSheet, Button, Text } from "react-native";
import { Camera, CameraView } from "expo-camera";

const App = () => {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const intervalRef = useRef<number | null>(null);
  const cameraRef = useRef<CameraView | null>(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === "granted");
    })();

    const ws = new WebSocket("ws://192.168.178.25:8000");
    ws.onopen = () => console.log("WebSocket Connected");
    ws.onclose = () => console.log("WebSocket Disconnected");
    ws.onerror = (err) => console.error("WebSocket Error:", err);
    setWebsocket(ws);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (ws) ws.close();
    };
  }, []);

  const startStreaming = async () => {
    if (!cameraRef.current) {
      console.error("Camera not initialized");
      return;
    }

    setIsStreaming(true);

    intervalRef.current = window.setInterval(async () => {
      if (!cameraRef.current) {
        console.error("Camera not initialized");
        return;
      }

      const photo = await cameraRef.current.takePictureAsync({
        base64: true,
        quality: 0.3,
      });

      if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not connected");
        return;
      }

      if (!photo) {
        console.error("Photo is undefined");
        return;
      }

      websocket.send(JSON.stringify({
        frame: photo.base64,
        timestamp: Date.now(),
      }));
      console.log("Frame sent to server");
    }, 2000); // Captura un frame cada 2 segundos
  };

  const stopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current); // Detener el intervalo
      intervalRef.current = null;
    }
    setIsStreaming(false);
    console.log("Streaming stopped");
  };

  if (hasPermission === null) {
    return <Text>Requesting Camera Permission</Text>;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} />
      <View style={styles.buttonContainer}>
        {!isStreaming ? (
          <Button title="Start Streaming" onPress={startStreaming} />
        ) : (
          <Button title="Stop Streaming" onPress={stopStreaming} />
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F9F9F9", // Fondo claro
  },
  camera: {
    flex: 1,
    borderRadius: 20, // Bordes redondeados
    overflow: "hidden",
    margin: 10,
  },
  buttonContainer: {
    position: "absolute",
    bottom: 30,
    alignSelf: "center",
    backgroundColor: "#007AFF", // Azul icónico de Apple
    borderRadius: 25,
    paddingVertical: 12,
    paddingHorizontal: 30,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
});

export default App;
