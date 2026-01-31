import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: "Home" }} />
      <Stack.Screen name="study" options={{ title: "Study" }} />
      <Stack.Screen name="result" options={{ title: "Result" }} />
    </Stack>
  );
}
