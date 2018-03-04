package com.cdeleo.ytman.thumbnails;

import java.awt.Graphics2D;

public class ContextFrame implements AutoCloseable {

  private final Graphics2D c;

  public ContextFrame(Graphics2D c) {
    this.c = (Graphics2D) c.create();
  }

  @Override
  public void close() throws Exception {
    c.dispose();
  }

  public Graphics2D get() {
    return c;
  }
}
