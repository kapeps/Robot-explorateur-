<template>
  <v-app id="inspire">

    <v-navigation-drawer v-model="drawer" fixed app clipped>
      <v-list dense>
        <v-list-tile to="/">
          <v-list-tile-action>
            <v-icon>home</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Home</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile to="/chart">
          <v-list-tile-action>
            <v-icon>show_chart</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Chart</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile to="/light">
          <v-list-tile-action>
            <v-icon>highlight</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Light</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile to="/led">
          <v-list-tile-action>
            <v-icon>mdi-lightbulb</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Led</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
        <v-list-tile to="/motor">
          <v-list-tile-action>
            <v-icon>mdi-lightbulb</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>Motor</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar color="red accent-4" dark fixed app clipped-left>
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-title>Robot Explorateur</v-toolbar-title>
    </v-toolbar>

    <v-content>
      <v-container fluid fill-height>
        <router-view></router-view>
      </v-container>
    </v-content>


    <v-footer color="red accent-4" app fixed>
      <span class="white--text">&copy;CentraleSupelec         La Frabrique  Test</span>
    </v-footer>
    
  </v-app>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      drawer: null
    };
  }
};
</script>
