Repair a real defect in the Java project Mockito (Defects4J bug Mockito-9).

The working directory is a checkout of the buggy version. Layout:
  - production sources : src
  - test sources       : test   (read-only for you)

The sources currently compile. The following developer test(s) fail because of
the defect:

  - org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodStubbed
  - org.mockitousage.constructor.CreatingMocksWithConstructorTest::testCallsRealInterfaceMethod
  - org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodReturnsDefault

Failure output from the initial test run:

```
--- org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodStubbed
org.mockito.exceptions.base.MockitoException: 
Cannot call abstract real method on java object!
Calling real methods is only possible when mocking non abstract method.
  //correct example:
  when(mockOfConcreteClass.nonAbstractMethod()).thenCallRealMethod();
	at org.mockito.exceptions.Reporter.cannotCallAbstractRealMethod(Reporter.java:583)
	at org.mockito.internal.invocation.InvocationImpl.callRealMethod(InvocationImpl.java:110)
	at org.mockito.internal.stubbing.answers.CallsRealMethods.answer(CallsRealMethods.java:36)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:93)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:38)
	at org.mockito.internal.creation.cglib.MethodInterceptorFilter.intercept(MethodInterceptorFilter.java:59)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing$$EnhancerByMockitoWithCGLIB$$4ff3327a.name(<generated>)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest.abstractMethodStubbed(CreatingMocksWithConstructorTest.java:119)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.internal.runners.statements.RunBefores.evaluate(RunBefores.java:26)
	at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:27)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
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
--- org.mockitousage.constructor.CreatingMocksWithConstructorTest::testCallsRealInterfaceMethod
org.mockito.exceptions.base.MockitoException: 
Cannot call abstract real method on java object!
Calling real methods is only possible when mocking non abstract method.
  //correct example:
  when(mockOfConcreteClass.nonAbstractMethod()).thenCallRealMethod();
	at org.mockito.exceptions.Reporter.cannotCallAbstractRealMethod(Reporter.java:583)
	at org.mockito.internal.invocation.InvocationImpl.callRealMethod(InvocationImpl.java:110)
	at org.mockito.internal.stubbing.answers.CallsRealMethods.answer(CallsRealMethods.java:36)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:93)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:38)
	at org.mockito.internal.creation.cglib.MethodInterceptorFilter.intercept(MethodInterceptorFilter.java:59)
	at $java.util.List$$EnhancerByMockitoWithCGLIB$$9db60fc7.get(<generated>)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest.testCallsRealInterfaceMethod(CreatingMocksWithConstructorTest.java:126)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:50)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:47)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.internal.runners.statements.RunBefores.evaluate(RunBefores.java:26)
	at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:27)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:325)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:78)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:57)
	at org.junit.runners.ParentRunner$3.run(ParentRunner.java:290)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:71)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:288)
	at org.junit.runners.ParentRunner.access$000(ParentRunner.java:58)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:268)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:363)
	at junit.framework.JUnit4TestAdapter.run(JUnit4TestAdapter.java:38)
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
--- org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodReturnsDefault
org.mockito.exceptions.base.MockitoException: 
Cannot call abstract real method on java object!
Calling real methods is only possible when mocking non abstract method.
  //correct example:
  when(mockOfConcreteClass.nonAbstractMethod()).thenCallRealMethod();
	at org.mockito.exceptions.Reporter.cannotCallAbstractRealMethod(Reporter.java:583)
	at org.mockito.internal.invocation.InvocationImpl.callRealMethod(InvocationImpl.java:110)
	at org.mockito.internal.stubbing.answers.CallsRealMethods.answer(CallsRealMethods.java:36)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:93)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:38)
	at org.mockito.internal.creation.cglib.MethodInterceptorFilter.intercept(MethodInterceptorFilter.java:59)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing$$EnhancerByMockitoWithCGLIB$$4ff3327a.name(<generated>)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing.fullName(CreatingMocksWithConstructorTest.java:106)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing$$EnhancerByMockitoWithCGLIB$$4ff3327a.CGLIB$fullName$1(<generated>)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing$$EnhancerByMockitoWithCGLIB$$4ff3327a$$FastClassByMockitoWithCGLIB$$9e635d13.invoke(<generated>)
	at org.mockito.cglib.proxy.MethodProxy.invokeSuper(MethodProxy.java:216)
	at org.mockito.internal.creation.cglib.DelegatingMockitoMethodProxy.invokeSuper(DelegatingMockitoMethodProxy.java:19)
	at org.mockito.internal.invocation.realmethod.DefaultRealMethod.invoke(DefaultRealMethod.java:21)
	at org.mockito.internal.invocation.realmethod.CleanTraceRealMethod.invoke(CleanTraceRealMethod.java:30)
	at org.mockito.internal.invocation.InvocationImpl.callRealMethod(InvocationImpl.java:112)
	at org.mockito.internal.stubbing.answers.CallsRealMethods.answer(CallsRealMethods.java:36)
	at org.mockito.internal.handler.MockHandlerImpl.handle(MockHandlerImpl.java:93)
	at org.mockito.internal.handler.NullResultGuardian.handle(NullResultGuardian.java:29)
	at org.mockito.internal.handler.InvocationNotifierHandler.handle(InvocationNotifierHandler.java:38)
	at org.mockito.internal.creation.cglib.MethodInterceptorFilter.intercept(MethodInterceptorFilter.java:59)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest$AbstractThing$$EnhancerByMockitoWithCGLIB$$4ff3327a.fullName(<generated>)
	at org.mockitousage.constructor.CreatingMocksWithConstructorTest.abstractMethodReturnsDefault(CreatingMocksWithConstructorTest.java:113)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorI
... (truncated)
```

Your task: find the root cause and fix it in src, then verify with
`defects4j compile` and `defects4j test` that the failing test(s) pass and that
no other developer test broke.
