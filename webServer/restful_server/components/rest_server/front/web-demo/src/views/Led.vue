<template>
  <v-container>
    <v-layout text-xs-center wrap>
      <v-flex xs12 sm6 offset-sm3>
        <v-card>
          <v-card-text>
            <v-container fluid grid-list-lg>
              <v-layout row wrap>
                <v-flex xs9>
                  <v-slider v-model="onTime" :max="2000" label="On time"></v-slider>
                </v-flex>
                <v-flex xs3>
                  <v-text-field v-model="onTime" class="mt-0" type="number"></v-text-field>
                </v-flex>
                <v-flex xs9>
                  <v-slider v-model="offTime" :max="2000" label="Off time"></v-slider>
                </v-flex>
                <v-flex xs3>
                  <v-text-field v-model="offTime" class="mt-0" type="number"></v-text-field>
                </v-flex>
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
    return { onTime: 1000, offTime: 1000};
  },
  methods: {
    set_led: function() {
      this.$ajax
        .post("/api/v1/led", {
          onTime: this.onTime,
          offTime: this.offTime,
        })
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          console.log(error);
        });
    }
  }
};
</script>
