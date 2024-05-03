import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
} from "react-native";
import { globalStyles } from "../../styles/global";
import { EvilIcons } from "@expo/vector-icons";

export default function Campaigns() {
  return (
    <View style={globalStyles.campaingsContainer}>
      <View style={globalStyles.searchBar}>
        <View>
          <TextInput
            style={styles.searchInput}
            placeholder="Search.."
          ></TextInput>
        </View>
      </View>
      <View style={globalStyles.arcTab}>
        <TouchableOpacity style={styles.startCampaignBtn}>
          <Text style={styles.compaignBtnText}>Start a new campaingn</Text>
          <EvilIcons
            style={styles.compaignBtnIcon}
            name="arrow-right"
            size={34}
            color="black"
          />
        </TouchableOpacity>
        <Text style={globalStyles.pageTitle}>Donate to a campaign</Text>
        <TouchableOpacity style={styles.campaign}>
          <View style={styles.campaignDetails}>
            <Text style={styles.campaignTitle}>
              Cyclone freddy ndilande food items
            </Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>Country:</Text> Malawi
            </Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>By: </Text>Pemphero Mphande
            </Text>
          </View>
          <View>
            <Text style={[styles.compaignInfoText, styles.compaignInfoTitle]}>
              Closing on:
            </Text>
            <Text style={styles.compaignInfoText}>24/11/2023</Text>
          </View>
        </TouchableOpacity>
        <TouchableOpacity style={styles.campaign}>
          <View style={styles.campaignDetails}>
            <Text style={styles.campaignTitle}>Food for the sick</Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>Country:</Text> Zambia
            </Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>By: </Text>Yo Mamps Yo
            </Text>
          </View>
          <View>
            <Text style={[styles.compaignInfoText, styles.compaignInfoTitle]}>
              Closing on:
            </Text>
            <Text style={styles.compaignInfoText}>24/11/2023</Text>
          </View>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  searchInput: {
    backgroundColor: "#FFF",
    padding: 10,
    paddingHorizontal: 20,
    borderRadius: 15,
  },
  startCampaignBtn: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 15,
    paddingHorizontal: 20,
    borderRadius: 15,
    backgroundColor: "#B21F5E",
    marginBottom: 15,
  },
  compaignBtnText: {
    fontSize: 18,
    fontFamily: "nunito-bold",
    color: "#FFF",
  },
  compaignBtnIcon: {
    fontFamily: "nunito-bold",
    color: "#FFF",
  },
  campaign: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 10,
    paddingHorizontal: 20,
    borderRadius: 15,
    backgroundColor: "#FFF",
    elevation: 1, // Adjust the elevation to control the shadow depth
    marginVertical: 5,
  },
  campaignDetails: { flex: 1 },
  campaignTitle: {
    fontFamily: "nunito-bold",
  },
  compaignInfoText: {
    fontSize: 12,
    color: "#666",
  },
  compaignInfoTitle: { fontFamily: "nunito-bold" },
});
