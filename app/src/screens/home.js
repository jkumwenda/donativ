import React from "react";
import { StatusBar } from "expo-status-bar";
import { StyleSheet, Text, View, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { MaterialIcons } from "@expo/vector-icons";
import { SimpleLineIcons } from "@expo/vector-icons";
import { globalStyles } from "../styles/global";
import Logo from "../components/logo";

export default function Home({ navigation }) {
  const pressHandler = () => {
    navigation.navigate("Login");
  };
  const pressHandlerCampaigns = () => {
    navigation.navigate("Campaigns");
  };
  const pressHandlerOrganisations = () => {
    navigation.navigate("Organisations");
  };

  return (
    <View style={globalStyles.container}>
      <Logo />
      <View style={styles.space}></View>
      <View style={styles.blueTab}>
        <View>
          <Text style={styles.blueTabText}>Make an impact</Text>
          <Text style={styles.blueTabTitle}>Today</Text>
        </View>
        <View>
          <TouchableOpacity style={styles.donateBtn}>
            <Text style={globalStyles.btnTextNoIcon}>Donate</Text>
          </TouchableOpacity>
        </View>
      </View>
      <View style={styles.space}></View>
      <View style={styles.compaignOrgs}>
        <TouchableOpacity
          style={styles.compaignOrgTab}
          onPress={pressHandlerCampaigns}
        >
          <MaterialIcons name="campaign" size={24} color="black" />
          <Text style={styles.campaignText}>Campains (1200)</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.compaignOrgTab}
          onPress={pressHandlerOrganisations}
        >
          <SimpleLineIcons name="organization" size={24} color="black" />
          <Text style={styles.campaignText}>Organisations (800)</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.space}></View>
      <Text style={globalStyles.pageTitle}>We have received!</Text>
      <View style={styles.space}></View>
      <View style={styles.clothing}>
        <View style={styles.icon}>
          <Ionicons name="shirt" size={48} color="#773B59" />
        </View>
        <View>
          <View>
            <Text style={[styles.clothingTitle, globalStyles.tabTitle]}>
              Clothing
            </Text>
            <Text style={globalStyles.tabText}>2,820 Pieces donated</Text>
          </View>
        </View>
      </View>
      <View style={styles.space}></View>
      <View style={styles.money}>
        <View style={styles.icon}>
          <Ionicons name="cash" size={48} color="#B21F5E" />
        </View>
        <View>
          <View>
            <Text style={[styles.moneyTitle, globalStyles.tabTitle]}>
              Money
            </Text>
            <Text style={globalStyles.tabText}>MWK 2.5 Billion donated</Text>
          </View>
        </View>
      </View>
      <View style={styles.space}></View>
      <View style={styles.food}>
        <View style={styles.icon}>
          <Ionicons name="fast-food" size={48} color="#2C6695" />
        </View>
        <View>
          <View>
            <Text style={[styles.foodTitle, globalStyles.tabTitle]}>Food</Text>
            <Text style={globalStyles.tabText}>8,000 Boxes</Text>
          </View>
        </View>
      </View>
      <View style={styles.space}></View>
      <TouchableOpacity style={globalStyles.btn} onPress={pressHandler}>
        <Ionicons name="heart" style={globalStyles.btnIcon} size={18} />
        <Text style={globalStyles.btnText}>Make an impact</Text>
      </TouchableOpacity>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    padding: 20,
  },
  blueTab: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#2C6695",
    padding: 15,
    borderRadius: 20,
  },
  blueTabTitle: {
    fontFamily: "nunito-bold",
    color: "#FFF",
    fontSize: 18,
    textTransform: "uppercase",
  },
  blueTabText: { fontFamily: "nunito-light", color: "#FFF", fontSize: 18 },

  donateBtn: {
    fontFamily: "nunito-bold",
    borderRadius: 10,
    justifyContent: "center",
    backgroundColor: "#B21F5E",
    paddingVertical: 5,
    paddingHorizontal: 15,
  },
  clothing: {
    display: "flex",
    flexDirection: "row",
    backgroundColor: "#fff",
    borderColor: "#773B59",
    borderWidth: 2,
    padding: 15,
    borderRadius: 20,
    alignItems: "center",
  },
  clothingTitle: {
    color: "#773B59",
  },

  money: {
    display: "flex",
    flexDirection: "row",
    backgroundColor: "#fff",
    borderColor: "#B21F5E",
    borderWidth: 2,
    padding: 15,
    borderRadius: 20,
    alignItems: "center",
  },
  moneyTitle: {
    color: "#B21F5E",
  },

  food: {
    display: "flex",
    flexDirection: "row",
    backgroundColor: "#fff",
    borderColor: "#2C6695",
    borderWidth: 2,
    padding: 15,
    borderRadius: 20,
    alignItems: "center",
  },
  foodTitle: {
    color: "#2C6695",
  },
  space: { height: 20 },
  tabFlex: {},
  icon: {
    marginRight: 20,
  },
  compaignOrgs: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  compaignOrgTab: { alignItems: "center" },
  campaignText: { fontFamily: "nunito-bold", color: "#2C6695" },
});
