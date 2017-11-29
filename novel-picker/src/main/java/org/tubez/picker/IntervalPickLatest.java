package org.tubez.picker;

import java.util.Calendar;

public class IntervalPickLatest {

	public static void main(String[] args) throws InterruptedException {
		PickLatest.pick();
		while(true){
			int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
			if (hour==15){
				PickLatest.pick();
			}
			Thread.sleep(60*60*1000);
		}

	}

}
