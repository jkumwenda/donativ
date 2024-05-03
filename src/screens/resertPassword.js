import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
} from "react-native";
import { MaterialCommunityIcons } from "@expo/vector-icons";
import { globalStyles } from "../styles/global";
import Logo from "../components/logo";

export default function ResetPassword() {
  return (
    <View style={globalStyles.flexContainer}>
      <Text style={styles.iconWrap}>
        <MaterialCommunityIcons
          name="form-textbox-password"
          size={64}
          color="#555"
        />
      </Text>

      <Text style={[globalStyles.pageTitleSmall, styles.Title]}>
        Let's reset password?
      </Text>
      <View style={globalStyles.formWrap}>
        <View style={styles.signupTextWrap}>
          <Text style={styles.signupText}>
            Please provide your correct email address and we we'll send you
            password change instructions.
          </Text>
        </View>
        <TextInput
          style={globalStyles.textInput}
          placeholder="Email"
        ></TextInput>
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
  iconWrap: {
    flexDirection: "column",
    justifyContent: "center",
  },
});
