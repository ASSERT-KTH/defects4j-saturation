Repair a real defect in the Java project JacksonDatabind (Defects4J bug JacksonDatabind-43).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.fasterxml.jackson.databind.objectid.TestObjectIdSerialization::testNullStringPropertyId

Failure output from the initial test run:

```
--- com.fasterxml.jackson.databind.objectid.TestObjectIdSerialization::testNullStringPropertyId
com.fasterxml.jackson.databind.JsonMappingException: Can not deserialize instance of java.lang.String out of VALUE_NULL token
 at [Source: {"value":3, "next":null, "id":null}; line: 1, column: 31] (through reference chain: com.fasterxml.jackson.databind.objectid.IdentifiableStringId["id"])
	at com.fasterxml.jackson.databind.JsonMappingException.from(JsonMappingException.java:216)
	at com.fasterxml.jackson.databind.DeserializationContext.mappingException(DeserializationContext.java:873)
	at com.fasterxml.jackson.databind.deser.std.StringDeserializer.deserialize(StringDeserializer.java:61)
	at com.fasterxml.jackson.databind.deser.std.StringDeserializer.deserialize(StringDeserializer.java:11)
	at com.fasterxml.jackson.databind.deser.impl.ObjectIdValueProperty.deserializeSetAndReturn(ObjectIdValueProperty.java:78)
	at com.fasterxml.jackson.databind.deser.impl.ObjectIdValueProperty.deserializeAndSet(ObjectIdValueProperty.java:71)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserializeFromObject(BeanDeserializer.java:341)
	at com.fasterxml.jackson.databind.deser.BeanDeserializerBase.deserializeWithObjectId(BeanDeserializerBase.java:1094)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:131)
	at com.fasterxml.jackson.databind.ObjectMapper._readMapAndClose(ObjectMapper.java:3789)
	at com.fasterxml.jackson.databind.ObjectMapper.readValue(ObjectMapper.java:2779)
	at com.fasterxml.jackson.databind.objectid.TestObjectIdSerialization.testNullStringPropertyId(TestObjectIdSerialization.java:317)
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

Classes the defect is known to be located in:

  - com.fasterxml.jackson.databind.deser.impl.ObjectIdValueProperty

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
