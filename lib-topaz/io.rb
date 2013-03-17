class IO
  class << self
    alias for_fd new
  end

  def <<(s)
    write(s)
    return self
  end

  def pos=(i)
    seek(i, IO::SEEK_SET)
  end

  def rewind
    seek(0, IO::SEEK_SET)
  end

  def each_line(sep = $/, limit = nil)
    sep, limit = get_sep_limit(sep, limit)
    if limit == 0
      raise ArgumentError.new("invalid limit: 0 for each_line")
    end
    while line = gets(sep, limit)
      yield line
    end
    self
  end

  def readline(sep = $/, limit = nil)
    line = gets(sep, limit)
    raise EOFError.new("end of file reached") if line.nil?
    line
  end

  def gets(sep = $/, limit = nil)
    if sep.nil?
      return read
    end
    sep, limit = get_sep_limit(sep, limit)
    raise IOError.new("closed stream") if closed?
    line = ""
    loop do
      c = getc
      break if c.nil? || c.empty?
      line << c
      break if c == sep || line.length == limit
    end
    $_ = line
    line.empty? ? nil : line
  end

  def readlines(sep = $/, limit = nil)
    lines = []
    each_line(sep, limit) { |line| lines << line }
    return lines
  end

  def self.read(name)
    File.open(name) do |f|
      f.read
    end
  end

  def self.readlines(name, *args)
    File.open(name) do |f|
      return f.readlines(*args)
    end
  end

  def self.popen(cmd, mode = 'r', opts = {}, &block)
    r, w = IO.pipe
    if mode != 'r' && mode != 'w'
      raise NotImplementedError.new("mode #{mode} for IO.popen")
    end

    pid = fork do
      if mode == 'r'
        r.close
        $stdout.reopen(w)
      else
        w.close
        $stdin.reopen(r)
      end
      exec(*cmd)
    end

    if mode == 'r'
      res = r
      w.close
    else
      res = w
      r.close
    end

    res.instance_variable_set("@pid", pid)
    block ? yield(res) : res
  end

  def pid
    @pid
  end

  # FIXME make private when available
  #private
  def get_sep_limit(sep, limit)
    if sep.is_a?(Fixnum) && limit.nil?
      limit = sep
      sep = $/
    end
    [sep, limit]
  end
end
