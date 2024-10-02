import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import Home from "../screens/home";
import Login from "../screens/login";
import Signup from "../screens/signup";
import ResetPassword from "../screens/resertPassword";
import Campaigns from "../screens/compaigns/campaigns";
import Organisations from "../screens/organisations/organisations";

const Stack = createNativeStackNavigator();

const screenOptions = {
  headerShown: true, // Show the header titles for all screens by default
  headerStyle: {
    backgroundColor: "#2C6695", // Default header background color
  },
  headerTitleStyle: {
    fontWeight: "bold", // Default header title style
    fontFamily: "nunito-bold",
  },
  headerTintColor: "white", // Default header text color
};

const MyStack = () => {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen
        name="Home"
        component={Home}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="Login"
        component={Login}
        options={{ headerTitle: "Log In" }}
      />
      <Stack.Screen
        name="Signup"
        component={Signup}
        options={{ headerTitle: "Sign Up" }}
      />
      <Stack.Screen
        name="ResetPassword"
        component={ResetPassword}
        options={{ headerTitle: "Reset Password" }}
      />
      <Stack.Screen
        name="Campaigns"
        component={Campaigns}
        options={{ headerTitle: "Active Campaigns" }}
      />
      <Stack.Screen
        name="Organisations"
        component={Organisations}
        options={{ headerTitle: "Organisations" }}
      />
    </Stack.Navigator>
  );
};

const Navigation = () => {
  return (
    <NavigationContainer>
      <MyStack />
    </NavigationContainer>
  );
};

export default Navigation;
