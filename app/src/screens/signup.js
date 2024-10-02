import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
} from "react-native";
import { globalStyles } from "../styles/global";
import Logo from "../components/logo";

export default function Signup() {
  return (
    <View style={globalStyles.flexContainer}>
      <Logo />
      <Text style={[globalStyles.pageTitleSmall, styles.Title]}>
        Ready to change lives?
      </Text>
      <View style={globalStyles.formWrap}>
        <View style={styles.signupTextWrap}>
          <Text style={styles.signupText}>
            Make sure you use the correct email address
          </Text>
        </View>
        <TextInput
          style={globalStyles.textInput}
          placeholder="First name"
        ></TextInput>
        <TextInput
          style={globalStyles.textInput}
          placeholder="Last name"
        ></TextInput>
        <TextInput
          style={globalStyles.textInput}
          placeholder="Email"
        ></TextInput>
        <TextInput
          style={globalStyles.textInput}
          placeholder="Password"
        ></TextInput>
        <View style={styles.terms}>
          <Text>By signing up you agree to our </Text>
          <TouchableOpacity>
            <Text style={styles.linkUnderline}>terms and conditions</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={globalStyles.btn}>
          <Text style={globalStyles.btnTextNoIcon}>Sign Up</Text>
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
    textAlign: "center",
  },
  linkText: {
    fontWeight: "bold",
    color: "#2C6695",
    textAlign: "right",
    marginTop: 8,
    fontSize: 13,
  },
  terms: {
    backgroundColor: "#c3c3c3c3",
    borderRadius: 15,
    padding: 20,
    marginVertical: 8,
  },
  linkUnderline: {
    textDecorationLine: "underline",
  },
});
