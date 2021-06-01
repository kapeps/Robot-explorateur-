#ifndef LED_BLINK_TASK_H
#define LED_BLINK_TASK_H




#define LED_PIN GPIO_NUM_2

void blinkTask( void * pvParameters);
void startBlinkTask();

static int onTime;
static int offTime;;


#endif //LED_BLINK_TASK