import React from "react";
import { View } from "react-native";
import { Image } from "react-native";
import { globalStyles } from "../styles/global";

export default function Logo() {
  return (
    <View style={globalStyles.logoContainer}>
      <Image
        style={globalStyles.logo}
        source={require("../../assets/images/logo.png")}
      />
    </View>
  );
}
