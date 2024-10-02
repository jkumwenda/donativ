import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { globalStyles } from "../styles/global";
import Logo from "../components/logo";

export default function Login({ navigation }) {
  const pressHandlerSignup = () => {
    navigation.navigate("Signup");
  };
  const pressHandlerResetPassword = () => {
    navigation.navigate("ResetPassword");
  };
  return (
    <View style={globalStyles.flexContainer}>
      <Logo />
      <Text style={[globalStyles.pageTitleSmall, styles.Title]}>
        Ready to change lives?
      </Text>
      <View style={globalStyles.formWrap}>
        <View style={styles.signupTextWrap}>
          <Text style={styles.signupText}>Don't have an account yet?</Text>
          <TouchableOpacity onPress={pressHandlerSignup}>
            <Text style={[styles.signupLinkText, styles.signupText]}>
              Sign up
            </Text>
          </TouchableOpacity>
          <Text style={styles.signupText}>instead</Text>
        </View>
        <TextInput
          style={globalStyles.textInput}
          placeholder="username"
        ></TextInput>
        <TextInput
          style={globalStyles.textInput}
          placeholder="password"
        ></TextInput>
        <TouchableOpacity style={globalStyles.btn}>
          <Text style={globalStyles.btnTextNoIcon}>Log In</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={pressHandlerResetPassword}>
          <Text style={styles.linkText}>Forgot your password?</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  Title: {
    textAlign: "center",
  },
  signupTextWrap: {
    flexDirection: "row",
    justifyContent: "center",
  },
  signupLinkText: {
    fontWeight: "bold",
    color: "#2C6695",
    paddingHorizontal: 5,
  },
  signupText: {
    paddingBottom: 10,
    verticalAlign: "middle",
    fontSize: 13,
  },
  linkText: {
    fontWeight: "bold",
    color: "#2C6695",
    textAlign: "right",
    marginTop: 8,
    fontSize: 13,
  },
});
