Repair a real defect in the Java project JacksonDatabind (Defects4J bug JacksonDatabind-59).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src/main/java
  - test sources       : src/test/java   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - com.fasterxml.jackson.databind.jsontype.TypeRefinementForMapTest::testMapKeyRefinement1384

Failure output from the initial test run:

```
--- com.fasterxml.jackson.databind.jsontype.TypeRefinementForMapTest::testMapKeyRefinement1384
com.fasterxml.jackson.databind.JsonMappingException: Can not find a (Map) Key deserializer for type [simple type, class com.fasterxml.jackson.databind.jsontype.TypeRefinementForMapTest$CompoundKey]
 at [Source: {"mapProperty":["java.util.HashMap",{"Compound|Key":"Value"}]}; line: 1, column: 37] (through reference chain: com.fasterxml.jackson.databind.jsontype.TestClass["mapProperty"])
	at com.fasterxml.jackson.databind.JsonMappingException.from(JsonMappingException.java:261)
	at com.fasterxml.jackson.databind.DeserializationContext.reportMappingException(DeserializationContext.java:1234)
	at com.fasterxml.jackson.databind.deser.DeserializerCache._handleUnknownKeyDeserializer(DeserializerCache.java:588)
	at com.fasterxml.jackson.databind.deser.DeserializerCache.findKeyDeserializer(DeserializerCache.java:168)
	at com.fasterxml.jackson.databind.DeserializationContext.findKeyDeserializer(DeserializationContext.java:499)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.createContextual(MapDeserializer.java:237)
	at com.fasterxml.jackson.databind.DeserializationContext.handleSecondaryContextualization(DeserializationContext.java:681)
	at com.fasterxml.jackson.databind.DeserializationContext.findContextualValueDeserializer(DeserializationContext.java:445)
	at com.fasterxml.jackson.databind.jsontype.impl.TypeDeserializerBase._findDeserializer(TypeDeserializerBase.java:188)
	at com.fasterxml.jackson.databind.jsontype.impl.AsArrayTypeDeserializer._deserialize(AsArrayTypeDeserializer.java:97)
	at com.fasterxml.jackson.databind.jsontype.impl.AsArrayTypeDeserializer.deserializeTypedFromObject(AsArrayTypeDeserializer.java:61)
	at com.fasterxml.jackson.databind.deser.std.MapDeserializer.deserializeWithType(MapDeserializer.java:387)
	at com.fasterxml.jackson.databind.deser.SettableBeanProperty.deserialize(SettableBeanProperty.java:497)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer._deserializeWithErrorWrapping(BeanDeserializer.java:511)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer._deserializeUsingPropertyBased(BeanDeserializer.java:397)
	at com.fasterxml.jackson.databind.deser.BeanDeserializerBase.deserializeFromObjectUsingNonDefault(BeanDeserializerBase.java:1196)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserializeFromObject(BeanDeserializer.java:314)
	at com.fasterxml.jackson.databind.deser.BeanDeserializer.deserialize(BeanDeserializer.java:148)
	at com.fasterxml.jackson.databind.ObjectMapper._readMapAndClose(ObjectMapper.java:3789)
	at com.fasterxml.jackson.databind.ObjectMapper.readValue(ObjectMapper.java:2833)
	at com.fasterxml.jackson.databind.jsontype.TypeRefinementForMapTest.testMapKeyRefinement1384(TypeRefinementForMapTest.java:125)
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

  - com.fasterxml.jackson.databind.JavaType
  - com.fasterxml.jackson.databind.type.CollectionLikeType
  - com.fasterxml.jackson.databind.type.MapLikeType
  - com.fasterxml.jackson.databind.type.TypeFactory

Your task: find the root cause and fix it in src/main/java, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
