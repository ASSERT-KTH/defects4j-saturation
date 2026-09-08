Repair a real defect in the Java project JacksonDatabind (Defects4J bug JacksonDatabind-50).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.fasterxml.jackson.databind.objectid.ObjectWithCreator1261Test::testObjectIds1261

Failure output from the initial test run:

```
--- com.fasterxml.jackson.databind.objectid.ObjectWithCreator1261Test::testObjectIds1261
com.fasterxml.jackson.databind.JsonMappingException: Can not deserialize instance of com.fasterxml.jackson.databind.objectid.ObjectWithCreator1261Test$Child out of START_ARRAY token
 at [Source: {
  "parents" : {
    "parent1" : {
      "@id" : 1,
      "children" : {
        "child1" : {
          "@id" : 2,
          "name" : "child1",
          "parent" : 1,
          "parentAsList" : [ 1 ]
        },
        "child2" : {
          "@id" : 3,
          "name" : "child2",
          "parent" : 4,
          "parentAsList" : [ 4 ]
        }
      },
      "favoriteChild" : null,
      "name" : "parent1"
    },
    "parent2" : {
      "@id" : 4,
      "children" : { },
      "favoriteChild" : null,
      "name" : "parent2"
    }
  }
}; line: 16, column: 28] (through reference chain: com.fasterxml.jackson.databind.objectid.Answer["parents"]->java.util.TreeMap["parent1"]->com.fasterxml.jackson.databind.objectid.Parent["children"]->java.util.LinkedHashMap["parentAsList"])
	at com.fasterxml.jackson.databind.JsonMappingException.from(JsonMappingException.java:261)
	at com.fasterxml.jackson.databind.DeserializationContext.reportMappingException(DeserializationContext.java:1233)
	at com.fasterxml.jackson.databind.DeserializationContext.handleUnexpectedToken(DeserializationContext.java:1121)
	at com.fasterxml.jackson.databind.DeserializationContext.handleUnexpectedToken(DeserializationContext.java:1074)
	at com.fasterxml.jackson.databind.deser.BeanDeserializerBase.deserializeFromArray(BeanDeserializerBase.java:1362)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer._deserializeOther(BeanDeserializer.java:173)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:149)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer._readAndBindStringKeyMap(MapDeserializer.java:507)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.deserialize(MapDeserializer.java:352)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.deserialize(MapDeserializer.java:27)
	at com.fasterxml.jackson.databind.deser.SettableBeanProperty.deserialize(SettableBeanProperty.java:490)
	at com.fasterxml.jackson.databind.deser.impl.FieldProperty.deserializeAndSet(FieldProperty.java:101)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserializeFromObject(BeanDeserializer.java:356)
	at com.fasterxml.jackson.databind.deser.BeanDeserializerBase.deserializeWithObjectId(BeanDeserializerBase.java:1156)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:145)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer._readAndBindStringKeyMap(MapDeserializer.java:507)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.deserialize(MapDeserializer.java:352)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.deserialize(MapDeserializer.java:27)
	at com.fasterxml.jackson.databind.deser.SettableBeanProperty.deserialize(SettableBeanProperty.java:490)
	at com.fasterxml.jackson.databind.deser.impl.FieldProperty.deserializeAndSet(FieldProperty.java:101)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.vanillaDeserialize(BeanDeserializer.java:275)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:139)
	at com.fasterxml.jackson.databind.ObjectMapper._readMapAndClose(ObjectMapper.java:3789)
	at com.fasterxml.jackson.databind.ObjectMapper.readValue(ObjectMapper.java:2833)
	at com.fasterxml.jackson.databind.objectid.ObjectWithCreator1261Test.testObjectIds1261(ObjectWithCreator1261Test.java:76)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at junit.framework.TestCase.runTest(TestCase.java:176)
	at junit.framework.TestCase.runBare(TestCase.java:141)
	at junit.framework.TestResult$1.protect(TestResult.java:122)
	at junit.framework.TestResult.runProtected(TestResult.java:142)
	at junit.framework.TestResult.run(TestResult.java:125)
	at junit.framework.TestCase.run(TestCase.java:129)
	at junit.framework.TestSuite.runTest(TestSuite.java:252)
	at junit.framework.TestSuite.run(TestSuite.java:247)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTestRunner.run(JUnitTestRunner.java:520)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeInVM(JUnitTask.java:1492)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:878)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeOrQueue(JUnitTask.java:1980)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.executeTests(JUnitTask.java:830)
	at org.apache.tools.ant.taskdefs.optional.junit.JUnitTask.execute(JUnitTask.java:2287)
	at org.apache.tools.ant.UnknownElement.execute(UnknownElement.java:291)
	at jdk.internal.reflect.GeneratedMethodAccessor4.invoke(Unknown Source)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.apache.tools.ant.dispatch.DispatchUtils.execute(DispatchUtils.java:106)
	at org.apache.tools.ant.Task.perform(Task.java:348)
	at org.apache.tools.ant.Target.execute(Target.java:392)
	at org.apache.tools.ant.Target.performTasks(Target.java:413)
	at org.apache.tools.ant.Project.executeSortedTargets(Project.java:1399)
	at org.apache.tools.ant.Project.executeTarget(Project.java:1368)
	at org.apache.tools.ant.helper.DefaultExecutor.executeTargets(DefaultExecutor.java:41)
	at org.apache.tools.ant.Project.executeTargets(Project.java:1251)
	at org.apache.tools.ant.Main.runBuild(Main.java:811)
	at org.apache.tools.ant.Main.startAnt(Main.java:217)
	at org.apache.tools.ant.launch.Launcher.run(Launcher.java:280)
	at org.apache.tools.ant.launch.Launcher.main(Launcher.java:109)
```

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
