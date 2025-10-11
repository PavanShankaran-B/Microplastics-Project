#include "esp_camera.h"
#include "WiFi.h"
#include "HTTPClient.h"

// ================== WIFI CREDENTIALS ==================
const char* ssid = "ae";        // <-- change this
const char* password = "Ezhu@2004";
 // <-- change this

// ================== SERVER URL ==================
// Replace with your Flask server IP + port
String serverUrl = "http://192.168.1.100:5000/upload";

// ================== CAMERA PIN CONFIG (AI Thinker ESP32-CAM) ==================
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ================== SETUP ==================
void setup() {
  Serial.begin(115200);
  delay(2000);   // small delay to stabilize boot

  // Connect WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi");
  Serial.print("📶 IP Address: ");
  Serial.println(WiFi.localIP());

  // Camera configuration
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Start small frame for stability (upgrade later if OK)
  config.frame_size = FRAMESIZE_QQVGA;   // 160x120
  config.jpeg_quality = 12;              // 0 = best, 63 = worst
  config.fb_count = 1;

  // Init camera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("❌ Camera init failed!");
    return;
  }
  Serial.println("✅ Camera init success!");
}

// ================== LOOP ==================
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Take picture
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("❌ Camera capture failed, retrying...");
      delay(2000);
      return; // try again next loop
    }

    // Send to server
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST((uint8_t *)fb->buf, fb->len);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("📩 Server response: " + response);
    } else {
      Serial.printf("❌ Error in sending POST: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
    esp_camera_fb_return(fb); // release buffer
  } else {
    Serial.println("⚠️ WiFi disconnected! Reconnecting...");
    WiFi.reconnect();
  }

  delay(5000); // wait 5s before next capture
}
