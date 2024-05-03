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

export default function Organisations() {
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
          <Text style={styles.compaignBtnText}>Create a new organisation</Text>
          <EvilIcons
            style={styles.compaignBtnIcon}
            name="arrow-right"
            size={34}
            color="black"
          />
        </TouchableOpacity>
        <Text style={globalStyles.pageTitle}>Donate to an organisation</Text>
        <TouchableOpacity style={styles.campaign}>
          <View style={styles.campaignDetails}>
            <Text style={styles.campaignTitle}>Tilitonse Children Home</Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>Country:</Text> Malawi
            </Text>
          </View>
        </TouchableOpacity>
        <TouchableOpacity style={styles.campaign}>
          <View style={styles.campaignDetails}>
            <Text style={styles.campaignTitle}>65 Home for the blind</Text>
            <Text style={styles.compaignInfoText}>
              <Text style={styles.compaignInfoTitle}>Country:</Text> Zambia
            </Text>
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
