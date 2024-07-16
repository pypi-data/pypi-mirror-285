<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
  <class>Dialog</class>
  <widget class="QDialog" name="Dialog">
    <property name="geometry">
      <rect>
        <x>0</x>
        <y>0</y>
        <width>400</width>
        <height>300</height>
      </rect>
    </property>
    <property name="windowTitle">
      <string>Dialog</string>
    </property>
    <widget class="QDialogButtonBox" name="bboxOkCancel">
      <property name="geometry">
        <rect>
          <x>30</x>
          <y>240</y>
          <width>341</width>
          <height>32</height>
        </rect>
      </property>
      <property name="orientation">
        <enum>Qt::Horizontal</enum>
      </property>
      <property name="standardButtons">
        <set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set>
      </property>
    </widget>
    <widget class="QLabel" name="lblHello">
      <property name="geometry">
        <rect>
          <x>90</x>
          <y>30</y>
          <width>191</width>
          <height>21</height>
        </rect>
      </property>
      <property name="text">
        <string>Hello HsPyLib Qt Application</string>
      </property>
    </widget>
  </widget>
  <resources/>
  <connections>
    <connection>
      <sender>bboxOkCancel</sender>
      <signal>accepted()</signal>
      <receiver>Dialog</receiver>
      <slot>accept()</slot>
      <hints>
        <hint type="sourcelabel">
          <x>248</x>
          <y>254</y>
        </hint>
        <hint type="destinationlabel">
          <x>157</x>
          <y>274</y>
        </hint>
      </hints>
    </connection>
    <connection>
      <sender>bboxOkCancel</sender>
      <signal>rejected()</signal>
      <receiver>Dialog</receiver>
      <slot>reject()</slot>
      <hints>
        <hint type="sourcelabel">
          <x>316</x>
          <y>260</y>
        </hint>
        <hint type="destinationlabel">
          <x>286</x>
          <y>274</y>
        </hint>
      </hints>
    </connection>
    <connection>
      <sender>bboxOkCancel</sender>
      <signal>accepted()</signal>
      <receiver>Dialog</receiver>
      <slot>accept()</slot>
      <hints>
        <hint type="sourcelabel">
          <x>204</x>
          <y>254</y>
        </hint>
        <hint type="destinationlabel">
          <x>164</x>
          <y>112</y>
        </hint>
      </hints>
    </connection>
    <connection>
      <sender>bboxOkCancel</sender>
      <signal>rejected()</signal>
      <receiver>Dialog</receiver>
      <slot>reject()</slot>
      <hints>
        <hint type="sourcelabel">
          <x>346</x>
          <y>258</y>
        </hint>
        <hint type="destinationlabel">
          <x>323</x>
          <y>130</y>
        </hint>
      </hints>
    </connection>
  </connections>
</ui>
