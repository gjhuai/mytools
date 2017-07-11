package org.tubez.picker;

public class IntervalPickLatest {

	public static void main(String[] args) throws InterruptedException {
		while(true){
			PickLatest.pick();
			Thread.sleep(60*60*1000);
		}

	}

}
