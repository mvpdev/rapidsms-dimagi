﻿package{	import flash.display.MovieClip;	import flash.events.*;	import flash.text.TextField;	import flash.text.TextFormat;		public class IconSpecifics extends MovieClip{		//private variables		private var style:TextFormat;		private var sub:TextFormat;		private var small:TextFormat;		private var header:TextFormat;				//constructor		public function IconSpecifics(e:XML) {			style = new TextFormat();			style.color = 0xFFFFFF;			style.font = "_sans";			style.size = 13;			small = new TextFormat();			small.color = 0xCCCCCC;			small.font = "_sans";			small.size = 8;			header = new TextFormat();			header.color = 0x999999;			header.font = "_sans";			header.bold = true;			header.size = 16;			sub = new TextFormat();			sub.color = 0xDD0000;			sub.font = "_sans";			sub.bold = true;			sub.size = 11;						drawSpecifics(e);		}				private function drawSpecifics(e:XML):void {			graphics.beginFill(0x000000,.7);			//creates shape of info bubble			graphics.lineTo(-5,0);			graphics.lineTo(15,-20);			graphics.lineTo(15,-140);			graphics.lineTo(245,-140);			graphics.lineTo(245,0);						graphics.lineTo(-5,0);			//graphics.drawRect(5,-50,200,100);			graphics.endFill();			graphics.beginFill(0x000000,.7);			//creates shape of info bubble			graphics.beginFill(0x000000,.7);			graphics.drawRect(15,-140, 230, 40);			graphics.endFill();			var teacherTXT:TextField						teacherTXT = new TextField();			teacherTXT.text = "School: " + e.Name			teacherTXT.setTextFormat(header);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -135;			addChild(teacherTXT);			teacherTXT = new TextField();			teacherTXT.text = "Head Master: " + e.Headmaster;			teacherTXT.setTextFormat(sub);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -120;			addChild(teacherTXT);						teacherTXT = new TextField();			teacherTXT.text = "Teacher Attendance: " + e.TeacherAttendance;			teacherTXT.setTextFormat(style);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -100;			addChild(teacherTXT);						teacherTXT = new TextField();			teacherTXT.text = "Boys Attendance: " + e.BoysAttendance; //boyStat			teacherTXT.setTextFormat(style);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -80;			addChild(teacherTXT);						teacherTXT = new TextField();			teacherTXT.text = "Girls Attendance: " + e.GirlsAttendance; //girlStat			teacherTXT.setTextFormat(style);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -60;			addChild(teacherTXT);						teacherTXT = new TextField();			teacherTXT.text = "Water Quality: " + e.WaterAvailability; //waterStat			teacherTXT.setTextFormat(style);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 40;			teacherTXT.y = -40;			addChild(teacherTXT);						teacherTXT = new TextField();			teacherTXT.text = e.Date; //waterStat			teacherTXT.setTextFormat(small);			teacherTXT.selectable = false;			teacherTXT.width = 200;			teacherTXT.x = 120;			teacherTXT.y = -20;			addChild(teacherTXT);					}	}}