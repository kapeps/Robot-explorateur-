<template>
  <v-container>
    <v-layout text-xs-center wrap>
      <v-flex xs12 sm6 offset-sm3>
        <v-card>
          <v-card-text>
            <v-container fluid grid-list-lg>
              <v-layout row wrap>
                <v-radio-group v-model="pick" row>
                  <v-radio label="Velocity control" value="velocity"></v-radio>
                  <v-radio label="Distance control" value="distance"></v-radio>
                  <v-radio label="Pregrogrammed movement" value="movement"></v-radio>
                </v-radio-group>
                <div>  
                    <v-container class="grey lighten-5">
                      <v-row no-gutters style="height: 150px;">
                        <v-col :key="align" :align-self="align"><v-spacer></v-col>
                        <v-col :key="align" :align-self="align">
                          <v-btn fab dark large color="red accent-4" @click="set_speed_forward">
                          <v-icon dark>mdi-arrow-up-bold</v-icon>
                          </v-btn>
                        </v-col>
                        <v-col :key="align" :align-self="align"><v-spacer></v-col>
                      </v-row>
                      <v-row no-gutters style="height: 150px;">
                        <v-col :key="align" :align-self="align">
                          <v-btn fab dark large color="red accent-4" @click="set_speed_left">
                          <v-icon dark>mdi-arrow-left-bold</v-icon>
                          </v-btn>
                        </v-col>
                        <v-col :key="align" :align-self="align">
                          <v-btn fab dark large color="red accent-4" @click="set_speed_backward">
                          <v-icon dark>mdi-arrow-down-bold</v-icon>
                          </v-btn>
                        </v-col>
                        <v-col :key="align" :align-self="align">
                          <v-btn fab dark large color="red accent-4" @click="set_speed_right">
                          <v-icon dark>mdi-arrow-right-bold</v-icon>
                          </v-btn>
                        </v-col>
                      </v-row>
                    </v-container>
                          <v-flex xs9>
                            <v-slider v-model="speed" :max="1000" label="Speed"></v-slider>
                          </v-flex>
                          <v-flex xs3>
                            <v-text-field v-model="speed" class="mt-0" type="number"></v-text-field>
                          </v-flex>
                      
                  </div>
              </v-layout>
            </v-container>
          </v-card-text>
          <v-btn fab dark large color="red accent-4" @click="set_led">
            <v-icon dark>check_box</v-icon>
          </v-btn>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
export default {
  data() {
    return { speed: 50};
  },
  methods: {
    set_speed_forward: function() {
      this.$ajax
        .post("/api/v1/speed", {
          speed: this.speed,
          direction: 0,
        })
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.log(error);
        })
    },
    
    set_speed_backward: function() {
      this.$ajax
        .post("/api/v1/speed", {
          speed: this.speed,
          direction: 1,
        })
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.log(error);
        })
    },

    set_speed_left: function() {
      this.$ajax
        .post("/api/v1/speed", {
          speed: this.speed,
          direction: 2,
        })
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.log(error);
        })
    },

    set_speed_right: function() {
      this.$ajax
        .post("/api/v1/speed", {
          speed: this.speed,
          direction: 3,
        })
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.log(error);
        })
    }
  }
};
</script>